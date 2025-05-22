import numpy as np

# Function to segment data
def segment_data(data, segment_length, total_length=180, stride=10):
    """
    Segments data into specified lengths with sliding windows
    segment_length in seconds, assuming data is sampled by RR intervals
    total_length is the total recording length in seconds
    stride is the step size in seconds between consecutive windows
    """
    # Convert RR intervals to cumulative time
    time_points = np.cumsum(data) / 1000  # convert from ms to seconds
    
    # Create segments
    segments = {}
    
    if segment_length == total_length:
        # Full recording - all data
        segments['full'] = data
        return segments
    
    # For sliding windows with stride
    window_count = 0
    start_time = 0
    
    # Continue creating windows until we can't fit a full segment_length window
    while start_time + segment_length <= total_length:
        end_time = start_time + segment_length
        
        # Find indices where time points fall within this window
        mask = (time_points >= start_time) & (time_points < end_time)
        
        if np.sum(mask) > 0:  # Only create segments with data
            segment_name = f"{segment_length}s_win{window_count}"
            segments[segment_name] = data[mask]
        
        # Move the start time forward by stride seconds
        start_time += stride
        window_count += 1
    
    # print(f"Created {len(segments)} segments of {segment_length} seconds with stride {stride} seconds.")
    # print(segments)
    return segments
