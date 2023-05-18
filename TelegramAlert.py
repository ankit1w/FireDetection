from telethon import TelegramClient as TelegramClientAsync
from telethon.sync import TelegramClient
from telethon.tl.types import InputPeerUser
import asyncio
import threading
import cv2
from io import BytesIO
import config

class TelegramAlert:

    def __init__(self):
        self.api_id = config.api_id
        self.api_hash =config.api_hash
        self.message = config.message
        self.phone = config.phone
        self.session_filename = self.phone[-10:]
        self.receiver_id = config.receiver_id
        self.peer_user = InputPeerUser(self.receiver_id, 0)

        self.initialize_client()

    def initialize_client(self):
        client = TelegramClient(self.session_filename, self.api_id, self.api_hash)
        client.connect()

        if not client.is_user_authorized():
            client.send_code_request(self.phone)
            client.sign_in(self.phone, input('Enter the code sent to your telegram account: '))
        client.disconnect()


    async def send_async(self, frame):
        async with TelegramClientAsync(self.session_filename, self.api_id, self.api_hash) as client:
            _, frame_bytes = cv2.imencode('.jpg', frame)

            frame_io = BytesIO(frame_bytes.tobytes())

            await client.send_file(self.peer_user, file=frame_io, caption=self.message)

    def send(self, frame):
        loop = asyncio.new_event_loop()

        def run_in_loop():
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.send_async(frame))
            loop.close()

        thread = threading.Thread(target=run_in_loop)
        thread.start()
