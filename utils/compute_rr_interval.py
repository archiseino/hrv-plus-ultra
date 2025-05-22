import neurokit2 as nk
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt

def convert_bvp_to_rr(bvp_signal, sampling_rate=64, visualize=False, task="T1", subject="S1"):
    """
    Converts a BVP/PPG signal to RR intervals using neurokit2 package
    
    Parameters:
    -----------
    bvp_signal : numpy.ndarray
        The raw BVP/PPG signal
    sampling_rate : int
        Sampling rate of the signal in Hz (default: 64)
    visualize : bool
        Whether to visualize the peak detection (default: False)
        
    Returns:
    --------
    rr_intervals : numpy.ndarray
        Array of RR intervals in milliseconds
    """
    

    # Step 1: Apply bandpass filter (0.5-8 Hz for heart rate range)
    nyquist = 0.5 * sampling_rate
    low = 0.5 / nyquist
    high = 3 / nyquist
    b, a = butter(2, [low, high], btype='band')
    filtered_bvp = filtfilt(b, a, bvp_signal)

    # Step 0: Upsample the signal to 200Hz using neurokit2
    target_rate = 100
    upsampled_bvp = nk.signal_resample(filtered_bvp, sampling_rate=sampling_rate, desired_sampling_rate=target_rate)
    upsampled_rate = target_rate
    
    # Step 1: Clean the BVP signal using neurokit2
    cleaned_bvp = nk.ppg_clean(upsampled_bvp, sampling_rate=upsampled_rate)
    
    # Step 2: Find peaks in the cleaned signal
    # nk.ppg_findpeaks returns info with identified peaks
    info = nk.ppg_findpeaks(cleaned_bvp, sampling_rate=upsampled_rate)
    peaks = info["PPG_Peaks"]
    
    # Step 3: Calculate RR intervals in milliseconds
    peak_times = peaks / upsampled_rate * 1000  # Convert to ms
    rr_intervals = np.diff(peak_times)
    
    # Step 4: Basic quality control - remove physiologically implausible intervals
    valid_mask = (rr_intervals > 300) & (rr_intervals < 2000)  # 30-200 bpm range
    rr_intervals = rr_intervals[valid_mask]

    # Optional visualization
    # if visualize and len(peaks) > 1:
    #     plt.figure(figsize=(15, 8))
        
    #     # Plot original signal
    #     time_axis_orig = np.arange(len(bvp_signal)) / sampling_rate
    #     plt.subplot(4, 1, 1)
    #     plt.plot(time_axis_orig, bvp_signal, 'b-', label='Original Signal')
    #     plt.title(f'Original BVP Signal ({sampling_rate}Hz) - Task: {task}, Subject: {subject}')
    #     plt.legend()
        
    #     # Plot upsampled signal
    #     time_axis_up = np.arange(len(upsampled_bvp)) / upsampled_rate
    #     plt.subplot(4, 1, 2)
    #     plt.plot(time_axis_up, upsampled_bvp, 'r-', label=f'Upsampled ({upsampled_rate}Hz)')
    #     plt.title('Upsampled BVP Signal')
    #     plt.legend()
        
    #     # Plot cleaned signal with peaks
    #     plt.subplot(4, 1, 3)
    #     plt.plot(time_axis_up, cleaned_bvp, 'g-', label='Cleaned BVP')
    #     plt.plot(peaks/upsampled_rate, cleaned_bvp[peaks], 'ko', label='Detected Peaks')
    #     plt.title('Cleaned BVP Signal with Detected Peaks')
    #     plt.legend()
        
    #     # Plot RR intervals
    #     plt.subplot(4, 1, 4)
    #     plt.plot(rr_intervals, 'b-')
    #     plt.title('RR Intervals')
    #     plt.ylabel('Time (ms)')
    #     plt.xlabel('Beat number')
    #     plt.tight_layout()
    #     plt.show()
        
    #     # Additional visualization: Show heart rate variability metrics
    #     try:
    #         # Convert RR intervals to seconds for HRV analysis
    #         rr_sec = rr_intervals / 1000
    #         hrv_indices = nk.hrv(rr_sec, sampling_rate=upsampled_rate, show=True)
    #         print("HRV Indices:")
    #         print(hrv_indices)
    #     except:
    #         print("Could not compute HRV indices.")
    
    return rr_intervals