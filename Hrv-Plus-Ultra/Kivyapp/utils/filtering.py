import scipy
import numpy as np

def preprocess_ppg(signal, fs = 30):
    """ Computes the Preprocessed PPG Signal, this steps include the following:
        1. Moving Average Smoothing
        2. Bandpass Filtering
        
        Parameters:
        ----------
        signal (numpy array): 
            The PPG Signal to be preprocessed
        fs (float): 
            The Sampling Frequency of the Signal
            
        Returns:
        --------
        numpy array: 
            The Preprocessed PPG Signal
    

    """ 

    # Additional lowpass tod remove high-frequency noise
    b, a = scipy.signal.butter(3, [0.9, 2.4], btype='band', fs=fs)
    filtered = scipy.signal.filtfilt(b, a, signal)
    
    # Normalize the signal
    normalized_signal = (filtered - np.min(filtered)) / (np.max(filtered) - np.min(filtered))


    return normalized_signal
