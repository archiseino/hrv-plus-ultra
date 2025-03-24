## HRV Using Physio Itera Dataset

Dataset performed by Mr. Martin using ITERA subject.

Procedure of doing recording is the subject doing the exercise first and then the recording is do after Post Exercise, as described in this Scenario.

#### Trivial

Why don't also record when doing exercise?

## Capture Scenario

| **Scenario** | **Description**                                   |
| :----------- | :------------------------------------------------ |
| 1            | Sit down with mask, post exercise                 |
| 2            | Sit down without mask, post exercise              |
| 3            | Sleeping position with face towards the camera    |
| 4            | Sleeping position without face towards the camera |
| 5            | Sit down with mask, relax                         |
| 6            | Sit down without mask, relax                      |

## Sampling Rate

- For video, it takes sampling rate 30 fps (1800 Images) / 60 Detik
- For GT ECG 200 Hz (12000 Value) / 60 Detik

## Notes

- For the way we doing, it it seems the procedure for the MMPD and Physio Itera are the same.
- Using Even Samples (2, 6) since the face is visible and we can observe the signal after exercise and resting.

- Ganti Mode, it seems using facial landmark doesn't detect the frame sometimes (For female subject, it seems based on the Mukena stuff)

- For facial detection, it seem the RGB signal are looking weird, but still produce the overall good RGB value,
- Try to limit / reduce the ROI / Bounding box of the face, the bounding box are to large at this point.
- The homework try to look up the factor to reduce the ROI

- Does the area roi is not fit perfectly fine? Or should I use the segmentation, but it will increase the process time.

### Irregularity between ECG and PPG

- It seems ECG can maintain the shape of the signal compare to PPG, but I can see it why, since ECG is comes from electricity signals from Heart, and PPG can have delays and artifacts, so one should note the PPG and ECG signal will be differ. Especially ECG will have strong regularity pattern and PPG will probably not.
- Hitam question, black people have hard time doing this haha
- But as long the estimation of HR are fine, I think it also fine.

## Dataset Outlier

Model Alina 2 / 6 can't be capture with mediapipe, one thought is that the glasses reflect light
