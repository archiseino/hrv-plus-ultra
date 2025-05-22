import numpy as np
from utils.compute_bsi import compute_bsi

# Function to calculate time-domain HRV features
def compute_hrv_features(rr_intervals):
    """
    Computes common time-domain HRV features from RR intervals
    """
    if len(rr_intervals) < 10:
        return {
            'meanNN': np.nan,
            'SDNN': np.nan,
            'meanHR': np.nan,
            'RMSSD': np.nan,
            'pNN50': np.nan,
            'BSI': np.nan
        }
        
    # Mean NN (RR) intervals in ms
    meanNN = np.mean(rr_intervals)
    
    # Standard deviation of NN intervals
    sdnn = np.std(rr_intervals)
    
    # Mean heart rate (bpm)
    mean_hr = 60000 / meanNN
    
    # RMSSD - Root Mean Square of Successive Differences
    diff_rr = np.diff(rr_intervals)
    rmssd = np.sqrt(np.mean(diff_rr**2))
    
    # pNN50 - Percentage of successive NN intervals differing by more than 50ms
    nn50 = sum(abs(diff_rr) > 50)
    pnn50 = (nn50 / len(diff_rr)) * 100 if len(diff_rr) > 0 else 0
    
    # Baevsky Stress Index
    bsi = compute_bsi(rr_intervals)
    
    return {
        'meanNN': meanNN,
        'SDNN': sdnn,
        'meanHR': mean_hr,
        'RMSSD': rmssd,
        'pNN50': pnn50,
        'BSI': bsi
    }
