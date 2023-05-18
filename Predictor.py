import numpy as np
import cv2
import time
from collections import deque
import os
from keras.models import load_model
from TelegramAlert import TelegramAlert
import config

class Predictor:

    def __init__(self, model_filepath):
        self.model = load_model(model_filepath)
        self.fire_queue = deque()
        self.fire_count = 0
        self.last_send_time = 0
        self.last_beep_time = 0
        self.telegram_alert = TelegramAlert()
        self.number_of_detections_to_consider = config.frame_rate*config.detection_threshold_in_seconds
        self.fire_detected_elibility_count = self.number_of_detections_to_consider * config.detection_eligibility_threshold_percentage / 100

    def is_fire(self, frame):
        x = cv2.resize(frame, (224, 224))

        x = np.expand_dims(x, axis=0)/255

        predictions = self.model.predict(x)[0]

        if max(predictions) > config.confidence_eligibility_threshold_percentage / 100:
            self.process_predictions(predictions, frame)

        return predictions 

    def process_predictions(self, predictions, frame):
        is_fire = predictions[0] > predictions[1]
        
        self.update_queue(frame, is_fire)

        if is_fire:
            self.alert(frame)

    def update_queue(self, frame, is_fire):
        if len(self.fire_queue) <= self.number_of_detections_to_consider:
            self.fire_queue.append(is_fire)
        else:
            self.fire_count -= self.fire_queue.popleft()
            self.fire_queue.append(is_fire)

        self.fire_count += is_fire
        
    def alert(self, frame):
        if time.time() > self.last_beep_time + .7:
            os.system("echo -e '\a'")
            self.last_beep_time = time.time()

        if self.fire_count > self.fire_detected_elibility_count:
            if time.time() > self.last_send_time + config.alert_message_frequency_in_minutes:
                self.telegram_alert.send(frame)
                self.last_send_time = time.time()
