import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

def compute_feature_correlations(feature_data, segment_names):
    """
    Compute Pearson correlations for multiple HRV features between different segments and full recordings.
    
    Parameters:
    -----------
    feature_data : dict
        Dictionary with feature names as keys, and each value is another dictionary
        with segment names as keys and numpy arrays as values
    segment_names : list
        List of segment names to process
        
    Returns:
    --------
    dict
        Dictionary of correlation results for each feature and segment
    """
    feature_correlations = {}
    
    for feature, segments in feature_data.items():
        feature_correlations[feature] = {}
        
        for segment in segment_names:
            if len(segments[segment]) == len(segments['full']):
                # Create mask for valid (non-NaN) values
                mask = ~np.isnan(segments[segment]) & ~np.isnan(segments['full'])
                
                # Need at least a few valid points for correlation
                if sum(mask) > 3:
                    corr, p_value = stats.pearsonr(
                        segments[segment][mask],
                        segments['full'][mask]
                    )
                    
                    feature_correlations[feature][segment] = {
                        'pearson_r': corr,
                        'p_value': p_value
                    }
    
    return feature_correlations

def plot_all_feature_correlations(feature_data, feature_correlations, hrv_features, 
                                 feature_display_names, segment_names):
    """
    Plot correlation scatterplots for all HRV features.
    
    Parameters:
    -----------
    feature_data : dict
        Dictionary with feature names as keys, and each value is another dictionary
        with segment names as keys and numpy arrays as values
    feature_correlations : dict
        Dictionary of correlation results from compute_feature_correlations
    hrv_features : list
        List of all feature names to plot
    feature_display_names : dict
        Dictionary mapping feature codes to human-readable display names
    segment_names : list
        List of segment names to plot
    """
    for feature in hrv_features:
        plt.figure(figsize=(18, 6))
        plt.suptitle(f"Correlation Analysis for {feature_display_names.get(feature, feature)}", fontsize=16)
        
        for i, segment in enumerate(segment_names):
            plt.subplot(1, len(segment_names), i+1)
            
            if segment in feature_correlations.get(feature, {}):
                # Create mask for valid data points
                valid_idx = ~np.isnan(feature_data[feature][segment]) & ~np.isnan(feature_data[feature]['full'])
                
                # Plot scatter points
                plt.scatter(feature_data[feature][segment][valid_idx], 
                           feature_data[feature]['full'][valid_idx], alpha=0.7)
                
                # Add best fit line
                x = feature_data[feature][segment][valid_idx]
                y = feature_data[feature]['full'][valid_idx]
                
                if len(x) > 1:
                    m, b = np.polyfit(x, y, 1)
                    plt.plot(x, m*x + b, 'r--')
                
                # Add title with correlation info
                plt.title(f"{segment} vs Full 3min\nr={feature_correlations[feature][segment]['pearson_r']:.2f}, p={feature_correlations[feature][segment]['p_value']:.3f}")
            else:
                plt.title(f"{segment} vs Full 3min\nInsufficient data")
                
            plt.xlabel(f"{segment} {feature}")
            plt.ylabel(f"Full 3min {feature}")
            plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.subplots_adjust(top=0.85)
        plt.show()


def compute_correlations(x_data, y_data, segment_names):
    """
    Compute Pearson correlations between different data segments and a reference value.
    
    Parameters:
    -----------
    x_data : dict
        Dictionary with segment names as keys and numpy arrays as values
    y_data : numpy array
        Reference data to correlate against
    segment_names : list
        List of segment names to process
        
    Returns:
    --------
    dict
        Dictionary of correlation results for each segment
    """
    correlations = {}
    
    for segment in segment_names:
        if len(x_data[segment]) == len(y_data):
            # Create mask for valid (non-NaN) values
            mask = ~np.isnan(x_data[segment]) & ~np.isnan(y_data)
            
            # Require at least a few valid points for correlation
            if sum(mask) > 3:  
                corr, p_value = stats.pearsonr(
                    x_data[segment][mask], 
                    y_data[mask]
                )
                
                correlations[segment] = {
                    'pearson_r': corr,
                    'p_value': p_value
                }
    
    return correlations


def plot_correlation_comparison(x_data, y_data, segment_names, correlations, 
                               title_prefix="", x_label_prefix="", 
                               y_label="Full 3min BSI", figsize=(18, 6)):
    """
    Plot correlation scatterplots with regression lines for multiple data segments.
    
    Parameters:
    -----------
    x_data : dict
        Dictionary with segment names as keys and numpy arrays as values
    y_data : numpy array
        Reference data to plot on y-axis
    segment_names : list
        List of segment names to plot
    correlations : dict
        Dictionary of correlation results from compute_correlations
    title_prefix : str, optional
        Prefix for plot titles
    x_label_prefix : str, optional
        Prefix for x-axis labels
    y_label : str, optional
        Label for y-axis
    figsize : tuple, optional
        Figure size
    """
    plt.figure(figsize=figsize)

    for i, segment in enumerate(segment_names):
        plt.subplot(1, len(segment_names), i+1)
        
        if segment in correlations:
            # Create mask for valid data points
            valid_idx = ~np.isnan(x_data[segment]) & ~np.isnan(y_data)
            
            # Plot scatter points
            plt.scatter(x_data[segment][valid_idx], y_data[valid_idx], alpha=0.7)
            
            # Add best fit line
            x = x_data[segment][valid_idx]
            y = y_data[valid_idx]
            
            if len(x) > 1:
                m, b = np.polyfit(x, y, 1)
                plt.plot(x, m*x + b, 'r--')
            
            # Add title with correlation info
            plt.title(f"{title_prefix}{segment} vs Full 3min\nr={correlations[segment]['pearson_r']:.2f}, p={correlations[segment]['p_value']:.3f}")
        else:
            plt.title(f"{title_prefix}{segment} vs Full 3min\nInsufficient data")
            
        plt.xlabel(f"{x_label_prefix}{segment}")
        plt.ylabel(y_label)
        plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

def summarize_feature_correlations(feature_correlations, hrv_features, segment_names, feature_display_names):
    """
    Create a summary table of correlation values for all features and segments.
    
    Parameters:
    -----------
    feature_correlations : dict
        Dictionary of correlation results from compute_feature_correlations
    hrv_features : list
        List of all feature names to summarize
    segment_names : list
        List of segment names to summarize
    feature_display_names : dict
        Dictionary mapping feature codes to human-readable display names
    """
    print("\nSummary of correlation values for all HRV features:")
    print("="*80)
    print(f"{'Feature':<30} | {'30s':<10} | {'1min':<10} | {'2min':<10} | {'Average':<10}")
    print("-"*80)
    
    # Calculate and display correlations for all features
    for feature in hrv_features:
        avg_corr = 0
        count = 0
        
        # Collect correlation values for each segment
        segment_corrs = []
        for segment in segment_names:
            if segment in feature_correlations.get(feature, {}):
                corr = feature_correlations[feature][segment]['pearson_r']
                segment_corrs.append(f"{corr:.2f}")
                avg_corr += abs(corr)
                count += 1
            else:
                segment_corrs.append("N/A")
        
        # Calculate average correlation
        avg_corr = avg_corr / count if count > 0 else float('nan')
        
        # Display feature with correlations
        display_name = feature_display_names.get(feature, feature)
        print(f"{display_name:<30} | {segment_corrs[0]:<10} | {segment_corrs[1]:<10} | {segment_corrs[2]:<10} | {avg_corr:.2f}")
    
    print("="*80)

def compute_method_correlations(method_data, reference_data, segment_names):
    """
    Compute correlations between method data segments and reference data.
    
    Parameters:
    -----------
    method_data : dict
        Dictionary with segment names as keys and numpy arrays as values
    reference_data : numpy.ndarray
        Reference data to compare against (e.g., full ground truth data)
    segment_names : list
        List of segment names to process
        
    Returns:
    --------
    dict
        Dictionary of correlation results with segment names as keys
    """
    correlations = {}
    
    for segment in segment_names:
        # Ensure equal lengths for comparison
        min_len = min(len(method_data[segment]), len(reference_data))
        
        if min_len > 3:  # Need at least a few valid points
            # Create mask for valid values (non-NaN)
            mask = ~np.isnan(method_data[segment][:min_len]) & ~np.isnan(reference_data[:min_len])
            
            if sum(mask) > 3:
                corr, p_value = stats.pearsonr(
                    method_data[segment][:min_len][mask],
                    reference_data[:min_len][mask]
                )
                
                correlations[segment] = {
                    'pearson_r': corr,
                    'p_value': p_value,
                    'valid_points': sum(mask)
                }
    
    return correlations
