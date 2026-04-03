## Extraction rPPG Value - Face Landmarker
# 
# Tahapan ini merupakan tahpaan untuk mengambil dan menyimpan sinyal rPPG dari video dengan menggunakan metode Face Landmarker (mengambil area pipi kiri dan pipi kanan)
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
import sys
import os

# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

## Import the rPPG methods
from rppg_methods.POS import POS
from rppg_methods.LGI import LGI
from rppg_methods.GREEN import GREEN
from rppg_methods.CHROM import CHROM
from rppg_methods.OMIT import OMIT

## Face Landmarker Setup

# Define the model
base_model="mediapipe_models/face_landmarker.task"

## Create Facelandmarker Object
base_options = python.BaseOptions(model_asset_path=base_model)
VisionRunningMode = mp.tasks.vision.RunningMode
options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    num_faces=1,
    running_mode = VisionRunningMode.IMAGE,
)
landmarker = vision.FaceLandmarker.create_from_options(options)

def get_cheek_rois(landmarks, image_shape):
    h, w, _ = image_shape
    left_cheek_indices = [116, 121, 187, 203]
    right_cheek_indices = [350, 345, 423, 411]

    left_cheek_points = [(int(landmarks[idx].x * w), int(landmarks[idx].y * h)) for idx in left_cheek_indices]
    right_cheek_points = [(int(landmarks[idx].x * w), int(landmarks[idx].y * h)) for idx in right_cheek_indices]

    left_cheek_rect = (
        min([pt[0] for pt in left_cheek_points]), min([pt[1] for pt in left_cheek_points]),
        max([pt[0] for pt in left_cheek_points]), max([pt[1] for pt in left_cheek_points])
    )
    # print("Left Cheek Rect:", left_cheek_rect)
    right_cheek_rect = (
        min([pt[0] for pt in right_cheek_points]), min([pt[1] for pt in right_cheek_points]),
        max([pt[0] for pt in right_cheek_points]), max([pt[1] for pt in right_cheek_points])
    )
    # print("Right Cheek Rect:", right_cheek_rect)

    return left_cheek_rect, right_cheek_rect


def extract_rgb_from_rect(rect, image):
    x_min, y_min, x_max, y_max = rect
    roi = image[y_min:y_max, x_min:x_max]
    return roi

### Preprocessing dan running method
def extract_rppg(video_path, output_dir, subject, task, fs=35):

    # Lists to store combined RGB values
    combined_r_signal, combined_g_signal, combined_b_signal = [], [], []

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
        result = landmarker.detect(mp_image)

        # Extract the face landmarks
        if result.face_landmarks:
            for face_landmark in result.face_landmarks:
                # Get cheek ROIs
                left_cheek_rect, right_cheek_rect = get_cheek_rois(face_landmark, image_rgb.shape)

                # Draw both cheek ROIs with rectangles
                cv2.rectangle(frame, (left_cheek_rect[0], left_cheek_rect[1]), (left_cheek_rect[2], left_cheek_rect[3]), (0, 255, 0), 2)
                cv2.rectangle(frame, (right_cheek_rect[0], right_cheek_rect[1]), (right_cheek_rect[2], right_cheek_rect[3]), (0, 255, 0), 2)

                # Extract the left and right cheek ROIs
                left_cheek_roi = extract_rgb_from_rect(left_cheek_rect, image_rgb)
                right_cheek_roi = extract_rgb_from_rect(right_cheek_rect, image_rgb)

                # Calculate mean pixel values for the RGB channels
                left_cheek_rgb = cv2.mean(left_cheek_roi)[:3]
                right_cheek_rgb = cv2.mean(right_cheek_roi)[:3]

                # Combine and average the RGB values from both cheeks
                combined_r = (left_cheek_rgb[0] + right_cheek_rgb[0]) / 2
                combined_g = (left_cheek_rgb[1] + right_cheek_rgb[1]) / 2
                combined_b = (left_cheek_rgb[2] + right_cheek_rgb[2]) / 2

                # Append the combined RGB values to the respective lists
                combined_r_signal.append(combined_r)
                combined_g_signal.append(combined_g)
                combined_b_signal.append(combined_b)

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
    pos_path = os.path.join(output_dir, f"Optimized_Landmark_{subject}_{task}-POS-rppg.npy")
    np.save(pos_path, pos_signal)
    print(f"Saved POS signal to: {pos_path}")

    chrom_path = os.path.join(output_dir, f"Optimized_Landmark_{subject}_{task}-CHROM-rppg.npy")
    np.save(chrom_path, chrom_signal)
    print(f"Saved CHROM signal to: {chrom_path}")

    lgi_path = os.path.join(output_dir, f"Optimized_Landmark_{subject}_{task}-LGI-rppg.npy")
    np.save(lgi_path, lgi_signal)
    print(f"Saved LGI signal to: {lgi_path}")

    green_path = os.path.join(output_dir, f"Optimized_Landmark_{subject}_{task}-GREEN-rppg.npy")
    np.save(green_path, green_signal)
    print(f"Saved GREEN signal to: {green_path}")

    omit_path = os.path.join(output_dir, f"Optimized_Landmark_{subject}_{task}-OMIT-rppg.npy")
    np.save(omit_path, omit_signal)
    print(f"Saved OMIT signal to: {omit_path}")

### Main method 
# Iterate the entire subject to convert RGB Signals from video to npy file format

# subjects = ["s41","s42", "s43", "s44", "s45", "s46", "s47", "s48", "s49", "s50"]
subjects = ["s51", "s52", "s53", "s54", "s55", "s56",]
# tasks = ["T1", "T3"]
tasks = ["T1",]

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

        


