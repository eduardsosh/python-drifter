from dataclasses import dataclass
import pickle
import time
import os

"""
Izveidosim klasi, kas glabas informaciju par masinu
Glabasim informaciju pickle formata
"""


@dataclass
class Carstate:
    tick: int
    x: float
    y: float
    angle: float
    
class Recorder:
    def __init__(self):
        self.recording = []

    def record_state(self,tick,x,y,angle):
        self.recording.append(Carstate(tick,x,y,angle))
        return

    def save_to_file(self):
        REC_DIR = 'recordings'
        # Ensure the directory exists
        if not os.path.exists(REC_DIR):
            os.makedirs(REC_DIR)

        # Construct the full file path
        filename = 'recording' + time.strftime("%Y%m%d-%H%M%S") + '.pkl'
        full_path = os.path.join(REC_DIR, filename)

        try:
            with open(full_path, 'wb') as f:
                pickle.dump(self.recording, f)
        except IOError:
            print("Kluda saglabajot failu")
            return
        return

    def clear_recording(self):
        self.recording.clear()
        return
    
    def load_recording(self, filename):
        REC_DIR = 'recordings'
        # Ensure the directory exists
        if not os.path.exists(REC_DIR):
            os.makedirs(REC_DIR)

        # Construct the full file path
        full_path = os.path.join(REC_DIR, filename)

        try:
            with open(full_path, 'rb') as f:
                self.recording = pickle.load(f)
                return self.recording
        except IOError:
            print("Kluda ieladejot failu")
            return
        return
    