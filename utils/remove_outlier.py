import numpy as np

def remove_outliers(data, method='IQR'):
    """
    Remove outliers from data.
    
    Args:
        data (array): Input data array
        method (str): Method for outlier detection ('IQR' for Interquartile Range)
        
    Returns:
        array: Data with outliers removed
    """
    if method == 'IQR':
        # Calculate Q1, Q3, and IQR
        q1 = np.percentile(data, 25)
        q3 = np.percentile(data, 75)
        iqr = q3 - q1
        
        # Define outlier bounds
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        # Filter out outliers
        filtered_data = data[(data >= lower_bound) & (data <= upper_bound)]
        
        # Report number of outliers removed
        n_outliers = len(data) - len(filtered_data)
        if n_outliers > 0:
            print(f"Removed {n_outliers} outliers using IQR method")
        
        return filtered_data
    else:
        print(f"Unknown outlier removal method: {method}")
        return data
