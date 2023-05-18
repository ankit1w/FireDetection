import cv2
import time
from Predictor import Predictor
import config

class FireDetection:
    def __init__(self, model_filepath, frame_rate, camera_channel):
        self.frame_rate = frame_rate
        self.predictor = Predictor(model_filepath)
        self.capture = cv2.VideoCapture(camera_channel)

    def start_detection(self):
        previous_capture = 0
        while True:
            try:
                time_elapsed = time.time() - previous_capture
                _, frame = self.capture.read()

                if time_elapsed > 1./self.frame_rate:
                    previous_capture = time.time()

                    self.process_frame(frame)
            except KeyboardInterrupt:
                print("\nExiting program")
                break

    def process_frame(self, frame):
        predictions = self.predictor.is_fire(frame)
        video_label = self.build_video_label(predictions)

        frame = cv2.putText(frame, video_label, (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
        cv2.imshow("Live Video", frame)
        cv2.waitKey(1)

    def build_video_label(self, predictions):
        if predictions[0] > predictions[1]:
            return f'Fire: {predictions[0]:f}'
        else:
            return f'No Fire: {predictions[1]:f}'

    def __del__(self):
        self.capture.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    fire_detection = FireDetection(config.model_filepath, config.frame_rate, config.camera_channel)
    fire_detection.start_detection()