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
    

recording = []

def record_state(tick,x,y,angle):
    recording.append(Carstate(tick,x,y,angle))
    return

def save_to_file():
    REC_DIR = 'recordings'
    # Ensure the directory exists
    if not os.path.exists(REC_DIR):
        os.makedirs(REC_DIR)

    # Construct the full file path
    filename = 'recording' + time.strftime("%Y%m%d-%H%M%S") + '.pkl'
    full_path = os.path.join(REC_DIR, filename)

    try:
        with open(full_path, 'wb') as f:
            pickle.dump(recording, f)
    except IOError:
        print("Kluda saglabajot failu")
        return
    return
