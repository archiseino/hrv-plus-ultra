import numpy as np

# Function to compute Baevsky Stress Index
def compute_bsi(rr_intervals):
    """
    Computes Baevsky Stress Index from RR intervals
    BSI = AMo / (2 * Mo * MxDMn)
    where:
    - AMo is the amplitude of the mode (% of RR intervals falling within mode bin)
    - Mo is the mode value (most common RR interval value)
    - MxDMn is the variation scope (difference between max and min RR intervals)
    """
    # Ensure there are enough intervals toa calculate BSI
    if len(rr_intervals) < 10:
        return np.nan
        
    # Calculate mode (Mo) - the most common RR interval value
    hist, bin_edges = np.histogram(rr_intervals, bins="fd")
    bin_idx = np.argmax(hist)
    Mo = (bin_edges[bin_idx] + bin_edges[bin_idx + 1]) / 2
    
    # Calculate AMo (amplitude of mode) - percentage of intervals corresponding to mode value
    # Using the stricter definition: percentage in the modal bin only
    AMo = 100 * hist[bin_idx] / len(rr_intervals)
    
    # Calculate MxDMn (variation range) - difference between max and min RR intervals
    MxDMn = np.max(rr_intervals) - np.min(rr_intervals)
    
    # Calculate Stress Index using revised Baevsky's formula with scaling factor
    stress_index = (AMo / 100) / (2 * Mo / 1000 * MxDMn / 1000) * 1000
    # This simplifies to: stress_index = AMo * 1000 / (2 * Mo * MxDMn / 1000)
    
    return stress_index
