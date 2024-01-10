from dataclasses import dataclass
import pickle
import time
import os
import clientside

"""
Izveidosim klasi, kas glabas informaciju par masinu
Glabasim informaciju pickle formata
"""
REC_DIR = 'recordings'

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

    def save_to_file(self,username,time):
        # Ensure the directory exists
        if not os.path.exists(REC_DIR):
            os.makedirs(REC_DIR)

        # Construct the full file path
        filename = f'{username}_{time}.pkl'
        full_path = os.path.join(REC_DIR, filename)

        try:
            with open(full_path, 'wb') as f:
                pickle.dump(self.recording, f)
        except IOError:
            print("Kluda saglabajot failu")
            return
        return filename

    def clear_recording(self):
        self.recording.clear()
        return
    
    def load_recording(self, filename):
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
        return filename
    
    # Online nav implementets :(
    def upload_recording(self, recording_name):
        file_path = os.path.join(REC_DIR, recording_name)
        clientside.send_file_to_server(file_path)
        return
    