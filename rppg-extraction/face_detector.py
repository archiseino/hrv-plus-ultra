## Extraction rPPG Value - Face Detector
# Tahapan ini merupakan tahpaan untuk mengambil dan menyimpan sinyal rPPG dari video dengan menggunakan metode FaceDetector (mengambil keseluruhan wajah)
# 
# ---
# 
# Metode rPPG berasal dari pyVHR toolkit
# ref: [https://github.com/phuselab/pyVHR/blob/master/pyVHR/BVP/methods.py](https://github.com/phuselab/pyVHR/blob/master/pyVHR/BVP/methods.py)

## Import Dependencies
import numpy as np
import mediapipe as mp
import pandas as pd
import cv2
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import matplotlib.pyplot as plt
import scipy
import os
import sys

# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

## Import the rPPG methods
from rppg_methods.POS import POS
from rppg_methods.LGI import LGI
from rppg_methods.GREEN import GREEN
from rppg_methods.CHROM import CHROM
from rppg_methods.OMIT import OMIT

# Define the model
base_model="mediapipe_models/blaze_face_short_range.tflite"

## Create faceDetector Object
base_options = python.BaseOptions(model_asset_path=base_model)
FaceDetector = mp.tasks.vision.FaceDetector
FaceDetectorOptions = mp.tasks.vision.FaceDetectorOptions
VisionRunningMode = mp.tasks.vision.RunningMode
options = FaceDetectorOptions(
    base_options=base_options,
    running_mode = VisionRunningMode.IMAGE,
)
detector = vision.FaceDetector.create_from_options(options)

# ### Preprocessing dan running method
def extract_rppg(video_path, output_dir, subject, task, fs=35):

    # Lists to store combined RGB values
    combined_r_signal, combined_g_signal, combined_b_signal = [], [], []
    margin_x=10 
    scaling_factor=0.8

    video_file = cv2.VideoCapture(video_path)

    while video_file.isOpened():
        ret, frame = video_file.read()
        if not ret:
            break

        # Convert image to RGB
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=image_rgb
        )

        # Face Detection
        result = detector.detect(mp_image)

        if result.detections:
            for detection in result.detections:

                ## Get the Bounding box
                bboxC = detection.bounding_box
                x, y, w, h = bboxC.origin_x, bboxC.origin_y, bboxC.width, bboxC.height

                new_x = int(x + margin_x)

                new_w = int(w * scaling_factor)
                new_h = int(h * scaling_factor)

                # Draw the rectangle
                cv2.rectangle(frame, (new_x, y), (new_x + new_w, y + new_h), (0, 255, 0), 2)

                ## Get the ROI
                face_roi = image_rgb[y:y+new_h, new_x:new_x+new_w]

                ## Calculate the Mean
                mean_rgb = cv2.mean(face_roi)[:3]
                
                # Append the combined RGB values to the respective lists
                combined_r_signal.append(mean_rgb[0])
                combined_g_signal.append(mean_rgb[1])
                combined_b_signal.append(mean_rgb[2])

        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Close the video file
    video_file.release()
    cv2.destroyAllWindows()

    ## Print the status
    print(f"Extracted {len(combined_r_signal)} frames for {subject}-{task}")

    ## Preparing RGB Signal Before Converting to rPPG
    rgb_signals = np.array([combined_r_signal, combined_g_signal, combined_b_signal])
    rgb_signals = rgb_signals.reshape(1, 3, -1)

    ## POS
    pos_signal = POS(rgb_signals, fps=fs)
    pos_signal = pos_signal.reshape(-1)

    ## CHROM
    chrom_signal = CHROM(rgb_signals)
    chrom_signal = chrom_signal.reshape(-1)

    ## LGI
    lgi_signal = LGI(rgb_signals)
    lgi_signal = lgi_signal.reshape(-1)

    ## GREEN
    green_signal = GREEN(rgb_signals)
    green_signal = green_signal.reshape(-1)

    ## OMIT
    omit_signal = OMIT(rgb_signals)
    omit_signal = omit_signal.reshape(-1)

    ## Save the RPPG as .npy
    pos_path = os.path.join(output_dir, f"{subject}_{task}-POS-rppg.npy")
    np.save(pos_path, pos_signal)
    print(f"Saved POS signal to: {pos_path}")

    chrom_path = os.path.join(output_dir, f"{subject}_{task}-CHROM-rppg.npy")
    np.save(chrom_path, chrom_signal)
    print(f"Saved CHROM signal to: {chrom_path}")

    lgi_path = os.path.join(output_dir, f"{subject}_{task}-LGI-rppg.npy")
    np.save(lgi_path, lgi_signal)
    print(f"Saved LGI signal to: {lgi_path}")

    green_path = os.path.join(output_dir, f"{subject}_{task}-GREEN-rppg.npy")
    np.save(green_path, green_signal)
    print(f"Saved GREEN signal to: {green_path}")

    omit_path = os.path.join(output_dir, f"{subject}_{task}-OMIT-rppg.npy")
    np.save(omit_path, omit_signal)
    print(f"Saved OMIT signal to: {omit_path}")


# Iterate the entire subject to convert RGB Signals from video to npy file format

subjects = ["s41","s42", "s43", "s44", "s45", "s46", "s47", "s48", "s49", "s50"]
tasks = ["T1", "T3"]

for subject in subjects:
    if not os.path.exists(f"dataset_numpy/{subject}"):
        print(f"Subject {subject} not found, skipping")
    
    for task in tasks:

        video_path = f"dataset_numpy/{subject}/vid_{subject}_{task}.avi"
        if os.path.exists(video_path):
            extract_rppg(
                video_path=video_path,
                output_dir=f"./{subject}",
                subject=subject,
                task=task,
                fs=35
            )

        


