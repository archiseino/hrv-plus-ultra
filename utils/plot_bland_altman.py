import numpy as np
import matplotlib.pyplot as plt


def bland_altman_plot(data1, data2, title, ylabel='Difference', xlabel='Mean', segment_name=None, save=True):
    """
    Creates a Bland-Altman plot to compare two measurement methods with enhanced annotations
    
    Args:
        data1, data2: Arrays of measurements to compare
        title: Plot title
        ylabel, xlabel: Axis labels
        segment_name: Name of segment for file saving (e.g., '30s')
        save: Whether to save the plot to file
    """
    mean = np.mean([data1, data2], axis=0)
    diff = data1 - data2
    md = np.mean(diff)
    sd = np.std(diff, axis=0)
    
    # Calculate coefficient of repeatability (CR) = 1.96 * SD of differences
    cr = 1.96 * sd
    
    # Calculate limits of agreement (LoA)
    upper_loa = md + cr
    lower_loa = md - cr
    
    # Calculate percentage of points within LoA
    within_loa = np.sum((diff >= lower_loa) & (diff <= upper_loa)) / len(diff) * 100
    
    # Create figure
    fig = plt.figure(figsize=(10, 6))
    
    # Create scatter plot with improved styling
    plt.scatter(mean, diff, alpha=0.8, s=50, color='#2f79c3', edgecolor='k', linewidth=0.5)
    
    # Add mean line and limits of agreement
    plt.axhline(md, color='#444444', linestyle='-', linewidth=1.5, label='Mean difference')
    plt.axhline(upper_loa, color='#c44e52', linestyle='--', linewidth=1.5, label='95% Limits of Agreement')
    plt.axhline(lower_loa, color='#c44e52', linestyle='--', linewidth=1.5)
    
    # Add reference line at y=0 (perfect agreement)
    plt.axhline(0, color='#54a24b', linestyle=':', linewidth=1, alpha=0.7, label='Line of equality')
    
    # Label plot
    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    
    # Add detailed annotations
    info_text = (
        f'Mean difference: {md:.2f}\n'
        f'Standard deviation: {sd:.2f}\n'
        f'Coefficient of repeatability: {cr:.2f}\n'
        f'95% Limits of Agreement: [{lower_loa:.2f}, {upper_loa:.2f}]\n'
        f'Points within LoA: {within_loa:.1f}%'
    )
    
    plt.annotate(info_text, xy=(0.05, 0.95), xycoords='axes fraction',
                bbox=dict(boxstyle="round,pad=0.5", fc="#f9f9f9", ec="gray", alpha=0.9),
                va='top', ha='left', fontsize=10)
    
    # Add legend
    plt.legend(loc='lower right')
    
    # Add grid for better readability
    plt.grid(True, alpha=0.3, linestyle=':')
    
    # Improve layout
    plt.tight_layout()
    
    # Save figure if requested
    # if save and segment_name:
        # filename = f"bland_altman_{segment_name}_vs_full.png"
        # plt.savefig(filename, dpi=300, bbox_inches='tight')
        # print(f"Saved Bland-Altman plot to {filename}")
    
    # return plt

def create_individual_bland_altman_plots(x_data, y_data, segment_names, correlations):
    """
    Create individual Bland-Altman plots for comparing each segment with the full recording.
    
    Parameters:
    -----------
    x_data : dict
        Dictionary with segment names as keys and numpy arrays as values
    y_data : numpy array
        Reference data to compare against (full recording)
    segment_names : list
        List of segment names to process
    correlations : dict
        Dictionary of correlation results from compute_correlations
    """
    print("\nAnalyzing agreement with Bland-Altman plots...")
    
    for segment in segment_names:
        if segment in correlations:
            valid_idx = ~np.isnan(x_data[segment]) & ~np.isnan(y_data)
            bland_altman_plot(
                x_data[segment][valid_idx],
                y_data[valid_idx],
                f"Bland-Altman Plot: {segment} vs Full 3min GT BSI",
                segment_name=segment
            )
            plt.show()

def create_feature_bland_altman_plots(feature_data, hrv_features, feature_correlations, 
                                     segment_names, feature_display_names):
    """
    Create Bland-Altman plots for all HRV features to assess agreement between
    short segments and full recordings.
    
    Parameters:
    -----------
    feature_data : dict
        Dictionary with feature names as keys, and each value is another dictionary
        with segment names as keys and numpy arrays as values
    hrv_features : list
        List of all feature names to analyze
    feature_correlations : dict
        Dictionary of correlation results from compute_feature_correlations
    segment_names : list
        List of segment names to analyze
    feature_display_names : dict
        Dictionary mapping feature codes to human-readable display names
    """
    print("\nGenerating Bland-Altman plots for all HRV features...")
    
    for feature in hrv_features:
        print(f"\nAnalyzing agreement for {feature_display_names.get(feature, feature)}...")
        
        # Combined plot for all segments
        plt.figure(figsize=(12, 8))
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
        markers = ['o', 's', '^']
        labels = {'30s': '30-second segments', '1min': '1-minute segments', '2min': '2-minute segments'}
        
        valid_segments = 0
        
        for i, segment in enumerate(segment_names):
            if segment in feature_correlations.get(feature, {}):
                valid_idx = ~np.isnan(feature_data[feature][segment]) & ~np.isnan(feature_data[feature]['full'])
                
                if sum(valid_idx) > 3:
                    # Calculate mean and difference
                    data1 = feature_data[feature][segment][valid_idx]
                    data2 = feature_data[feature]['full'][valid_idx]
                    mean = np.mean([data1, data2], axis=0)
                    diff = data1 - data2
                    md = np.mean(diff)
                    
                    # Plot scatter points
                    plt.scatter(mean, diff, alpha=0.7, s=40, color=colors[i], marker=markers[i], 
                               label=f"{labels[segment]} (mean diff: {md:.2f})")
                    
                    # Plot mean difference line
                    plt.axhline(md, color=colors[i], linestyle='--', alpha=0.7)
                    
                    valid_segments += 1
        
        # Only display the plot if we have valid segments
        if valid_segments > 0:
            # Add reference line at y=0 (perfect agreement)
            plt.axhline(0, color='k', linestyle='-', linewidth=1, alpha=0.5, label='Perfect agreement')
            
            plt.title(f"Combined Bland-Altman Plot: All Segment Lengths vs Full 3min {feature}", fontsize=14, fontweight='bold')
            plt.xlabel(f"Mean {feature} Value", fontsize=12)
            plt.ylabel(f"Difference (Segment - Full) {feature}", fontsize=12)
            plt.grid(True, alpha=0.3, linestyle=':')
            plt.legend(loc='best')
            plt.tight_layout()
            plt.show()
        else:
            print(f"  Not enough valid data for {feature} to create Bland-Altman plot")

def create_combined_bland_altman_plot(x_data, y_data, segment_names, correlations, 
                                     title="Combined Bland-Altman Plot", 
                                     xlabel="Mean BSI Value", 
                                     ylabel="Difference (Segment - Full)",
                                     figsize=(12, 8)):
    """
    Create a combined Bland-Altman plot to compare all segment lengths in one figure.
    
    Parameters:
    -----------
    x_data : dict
        Dictionary with segment names as keys and numpy arrays as values
    y_data : numpy array
        Reference data to compare against (full recording)
    segment_names : list
        List of segment names to process
    correlations : dict
        Dictionary of correlation results from compute_correlations
    title : str, optional
        Title for the plot
    xlabel : str, optional
        X-axis label
    ylabel : str, optional
        Y-axis label
    figsize : tuple, optional
        Figure size
    """
    plt.figure(figsize=figsize)

    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
    markers = ['o', 's', '^']
    labels = {'30s': '30-second segments', '1min': '1-minute segments', '2min': '2-minute segments'}

    for i, segment in enumerate(segment_names):
        if segment in correlations:
            valid_idx = ~np.isnan(x_data[segment]) & ~np.isnan(y_data)
            
            # Calculate mean and difference
            data1 = x_data[segment][valid_idx]
            data2 = y_data[valid_idx]
            mean = np.mean([data1, data2], axis=0)
            diff = data1 - data2
            md = np.mean(diff)
            
            # Plot scatter points
            plt.scatter(mean, diff, alpha=0.7, s=40, color=colors[i], marker=markers[i], 
                       label=f"{labels[segment]} (mean diff: {md:.2f})")
            
            # Plot mean difference line
            plt.axhline(md, color=colors[i], linestyle='--', alpha=0.7)

    # Add reference line at y=0 (perfect agreement)
    plt.axhline(0, color='k', linestyle='-', linewidth=1, alpha=0.5, label='Perfect agreement')

    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.grid(True, alpha=0.3, linestyle=':')
    plt.legend(loc='best')
    plt.tight_layout()
    plt.show()

def plot_method_comparisons(results_dict, reference_data, segment_names, method_names, 
                           feature_name="BSI", plot_bland_altman=True):
    """
    Create comparison plots for multiple methods against reference data.
    
    Parameters:
    -----------
    results_dict : dict
        Dictionary with method names as keys and result dictionaries as values
    reference_data : numpy.ndarray
        Reference data array to compare against
    segment_names : list
        List of segment names to plot
    method_names : list
        List of method names to include in plots
    feature_name : str, optional
        Name of the feature being plotted (default: "BSI")
    plot_bland_altman : bool, optional
        Whether to generate Bland-Altman plots for best methods (default: True)
    """
    # 1. Create correlation plots for each segment
    for segment in segment_names:
        plt.figure(figsize=(16, 6))
        plt.suptitle(f"Comparison of Methods: {segment} Segment vs Reference {feature_name}", fontsize=16)
        
        # Create subplots for each method
        for i, method in enumerate(method_names):
            plt.subplot(1, len(method_names), i+1)
            
            if segment in results_dict[method]['correlations']:
                # Get data for this method and segment
                method_data = results_dict[method]['bsi_values'][segment]
                
                # Find valid data points
                min_len = min(len(method_data), len(reference_data))
                mask = ~np.isnan(method_data[:min_len]) & ~np.isnan(reference_data[:min_len])
                
                if sum(mask) > 3:
                    x = method_data[:min_len][mask]
                    y = reference_data[:min_len][mask]
                    
                    # Plot scatter points
                    plt.scatter(x, y, alpha=0.7)
                    
                    # Add best fit line
                    if len(x) > 1:
                        m, b = np.polyfit(x, y, 1)
                        plt.plot(x, m*x + b, 'r--')
                    
                    # Add correlation info to title
                    corr = results_dict[method]['correlations'][segment]['pearson_r']
                    p_val = results_dict[method]['correlations'][segment]['p_value']
                    plt.title(f"{method}\nr={corr:.2f}, p={p_val:.3f}")
                else:
                    plt.title(f"{method}\nInsufficient data")
            else:
                plt.title(f"{method}\nNo correlation data")
                
            plt.xlabel(f"{segment} {method} {feature_name}")
            plt.ylabel(f"Reference {feature_name}")
            plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.subplots_adjust(top=0.85)
        plt.show()
    
    # 2. Find best method for each segment
    best_methods = {}
    for segment in segment_names:
        best_corr = 0
        best_method = None
        
        for method in method_names:
            if segment in results_dict[method]['correlations']:
                corr = abs(results_dict[method]['correlations'][segment]['pearson_r'])
                if corr > best_corr:
                    best_corr = corr
                    best_method = method
        
        best_methods[segment] = (best_method, best_corr)
    
    # 3. Display summary of best methods
    print(f"\nBest Methods for {feature_name} by Segment Length:")
    for segment, (method, corr) in best_methods.items():
        if method:
            print(f"  {segment}: {method} (r={corr:.2f})")
        else:
            print(f"  {segment}: No valid method found")
    
    # 4. Generate Bland-Altman plots if requested
    if plot_bland_altman:
        print(f"\nGenerating Bland-Altman plots for best methods...")
        
        for segment, (method, _) in best_methods.items():
            if method:
                print(f"  Creating Bland-Altman plot for {method} method, {segment} segment")
                
                method_data = results_dict[method]['bsi_values'][segment]
                min_len = min(len(method_data), len(reference_data))
                mask = ~np.isnan(method_data[:min_len]) & ~np.isnan(reference_data[:min_len])
                
                if sum(mask) > 3:
                    bland_altman_plot(
                        method_data[:min_len][mask],
                        reference_data[:min_len][mask],
                        f"Bland-Altman Plot: {method} {segment} {feature_name} vs Reference {feature_name}",
                        segment_name=f"{method}_{segment}_vs_reference",
                        ylabel=f"Difference ({method} - Reference)",
                        xlabel=f"Mean {feature_name}"
                    )
                    plt.show()