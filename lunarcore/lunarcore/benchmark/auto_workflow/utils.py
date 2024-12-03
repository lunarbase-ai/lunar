import numpy as np
import os
import warnings
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np
import os
import seaborn as sns
import warnings

from typing import List, Any


def open_file_create_dirs(file_path, mode='r'):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    return open(file_path, mode)


def empty_file(file_name: str):
    open_file_create_dirs(file_name, 'w').close()


def _save_or_show_plt(file_path: str = None):
    if file_path:
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        plt.savefig(file_path, bbox_inches='tight')
        return file_path
    else:
        plt.show()


def _save_plt_data(data: Any, image_file_path: str = None):
    if image_file_path:
        file_path = f'{image_file_path}.txt'
        with open_file_create_dirs(file_path, 'w') as file:
            file.write(str(data))


def histogram(data: List[int], title: str, xlabel: str, ylabel: str,
              file_path: str = None, bins: int = 8,
              integer_partition: bool = False,
              xaxis_integers: bool = False,
              title_fontsize: int = 18, label_fontsize: int = 16,
              tick_fontsize: int = 14, bold: bool = False):
    plt.clf()
    if integer_partition:
        d = np.diff(np.unique(data)).min()
        left_of_first_bin = data.min() - float(d)/2
        right_of_last_bin = data.max() + float(d)/2
        sns.histplot(data, bins=np.arange(left_of_first_bin, right_of_last_bin + d, d), kde=False)
    else:
        sns.histplot(data, bins=bins, kde=False)
    if xaxis_integers:
        plt.xticks(range(min(data), max(data)+1))
    
    fontweight = 'bold' if bold else 'normal'
    
    # Set title, xlabel, and ylabel with bold and fontsize options
    plt.title(title, fontsize=title_fontsize, fontweight=fontweight)
    plt.xlabel(xlabel, fontsize=label_fontsize, fontweight=fontweight)
    plt.ylabel(ylabel, fontsize=label_fontsize, fontweight=fontweight)
    
    # Set axis tick font sizes
    plt.xticks(fontsize=tick_fontsize)
    plt.yticks(fontsize=tick_fontsize)
    
    _save_plt_data(data, file_path)
    return _save_or_show_plt(file_path=file_path)


def linechart(x: List[int], ys: List[List[int]], ylabels: List[str],
              title: str, xlabel: str, ylabel: str,
              file_path: str = None, xaxis_integers: bool = False,
              xaxis_integers_step: int = None,
              title_fontsize: int = 18, xlabel_fontsize: int = 16,
              ylabel_fontsize: int = 16, legend_fontsize: int = 14,
              tick_fontsize: int = 14,
              ys_bar: List[int] = None, bar_label: str = "#Intents",
              bar_color: str = "lightgray", bar_alpha: float = 0.25,
              bar_width: float = 1.8):  # Add bar_width parameter
    
    plt.clf()
    if len(ys) != len(ylabels):
        warnings.warn(f"Plot '{title}' has different sizes of y values and y labels!")

    # Create the first axis for the line chart
    fig, ax1 = plt.subplots()

    # Plot the line chart on the first y-axis
    for label, y in zip(ylabels, ys):
        sns.lineplot(x=x, y=y, marker='s', label=label, ax=ax1)

    ax1.set_xlabel(xlabel, fontsize=xlabel_fontsize)
    ax1.set_ylabel(ylabel, fontsize=ylabel_fontsize)
    ax1.tick_params(axis='y', labelsize=tick_fontsize)
    ax1.set_title(title, fontsize=title_fontsize)

    if xaxis_integers:
        ax1.set_xticks(range(min(x), max(x) + 1, xaxis_integers_step))

    # Create the second y-axis for the bar chart
    ax2 = ax1.twinx()
    
    # Plot the bar chart on the second y-axis if provided
    if ys_bar is not None:
        ax2.bar(x, ys_bar, label=bar_label, color=bar_color, alpha=bar_alpha, width=bar_width)  # Set bar width
        ax2.set_ylabel(bar_label, fontsize=ylabel_fontsize)  # Set y-label for the bar chart
        ax2.tick_params(axis='y', labelsize=tick_fontsize)
        ax2.yaxis.set_major_locator(MaxNLocator(integer=True))

    # Create a combined legend
    lines, labels = ax1.get_legend_handles_labels()
    lines_bars, labels_bars = ax2.get_legend_handles_labels()
    
    ax1.legend(lines + lines_bars, labels + labels_bars, fontsize=legend_fontsize, loc='upper right')

    # Set axis tick font sizes
    ax1.tick_params(axis='x', labelsize=tick_fontsize)

    plt.tight_layout()  # Adjust the layout to make room for labels

    _save_plt_data([x, ys], file_path)
    return _save_or_show_plt(file_path=file_path)



# HISTOGRAM
# def linechart(x: List[int], ys: List[List[int]], ylabels: List[str],
#               title: str, xlabel: str, ylabel: str,
#               file_path: str = None, xaxis_integers: bool = False,
#               xaxis_integers_step: int = None,
#               title_fontsize: int = 18, xlabel_fontsize: int = 16,
#               ylabel_fontsize: int = 16, legend_fontsize: int = 14,
#               tick_fontsize: int = 14,
#               hist_data: List[int] = None, bins: int = 10, hist_color: str = 'lightgray',
#               hist_alpha: float = 0.6):
#     """
#     Draw a line chart with optional histogram in the background.

#     Parameters:
#     - hist_data: Data for the histogram (optional)
#     - bins: Number of bins for the histogram
#     - hist_color: Color of the histogram bars
#     - hist_alpha: Transparency level for the histogram (0.0 to 1.0)
#     """
#     plt.clf()

#     if len(ys) != len(ylabels):
#         warnings.warn(f"Plot '{title}' has different sizes of y values and y labels!")

#     # Plot histogram if data is provided
#     if hist_data:
#         plt.hist(hist_data, bins=bins, color=hist_color, alpha=hist_alpha, label='Histogram')

#     # Plot the line charts
#     for label, y in zip(ylabels, ys):
#         sns.lineplot(x=x, y=y, marker='s', label=label)

#     if xaxis_integers:
#         plt.xticks(range(min(x), max(x) + 1, xaxis_integers_step))

#     plt.title(title, fontsize=title_fontsize)
#     plt.xlabel(xlabel, fontsize=xlabel_fontsize)
#     plt.ylabel(ylabel, fontsize=ylabel_fontsize)
#     plt.legend(fontsize=legend_fontsize)

#     # Set axis tick font sizes
#     plt.xticks(fontsize=tick_fontsize)
#     plt.yticks(fontsize=tick_fontsize)

#     _save_plt_data([x, ys], file_path)
#     return _save_or_show_plt(file_path=file_path)


# BEFORE HISTOGRAM
# def linechart(x: List[int], ys: List[List[int]], ylabels: List[str],
#               title: str, xlabel: str, ylabel: str,
#               file_path: str = None, xaxis_integers: bool = False,
#               xaxis_integers_step: int = None,
#               title_fontsize: int = 18, xlabel_fontsize: int = 16,
#               ylabel_fontsize: int = 16, legend_fontsize: int = 14,
#               tick_fontsize: int = 14):
#     plt.clf()
#     if len(ys) != len(ylabels):
#         warnings.warn(f"Plot '{title}' has different sizes of y values and y labels!")

#     for label, y in zip(ylabels, ys):
#         sns.lineplot(x=x, y=y, marker='s', label=label)

#     if xaxis_integers:
#         plt.xticks(range(min(x), max(x) + 1, xaxis_integers_step))

#     plt.title(title, fontsize=title_fontsize)
#     plt.xlabel(xlabel, fontsize=xlabel_fontsize)
#     plt.ylabel(ylabel, fontsize=ylabel_fontsize)
#     plt.legend(fontsize=legend_fontsize)

#     # Set axis tick font sizes
#     plt.xticks(fontsize=tick_fontsize)
#     plt.yticks(fontsize=tick_fontsize)

#     _save_plt_data([x, ys], file_path)
#     return _save_or_show_plt(file_path=file_path)


def scatterplot3d(x: List[int], y: List[int], z: List[int], title: str,
                  xlabel: str, ylabel: str, zlabel: str,
                  file_path: str = None, labels: List = None,
                  axis_integers: bool = False):
    plt.clf()
    scatter = plt.scatter(x, y, c=z, s=350, cmap='Spectral', edgecolor='k', linewidth=0.5)
    cbar = plt.colorbar(scatter)
    cbar.set_label(zlabel)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    if labels:
        for i, label in enumerate(labels):
            plt.text(x[i] + 0.1, y[i], str(label), fontsize=10, ha='left', va='center')
    if axis_integers:
        plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
        plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    axis_lim_margins = 0.5
    plt.xlim(min(x) - axis_lim_margins, max(x) + axis_lim_margins)
    plt.ylim(min(y) - axis_lim_margins, max(y) + axis_lim_margins)
    _save_plt_data([x, y, z], file_path)
    return _save_or_show_plt(file_path=file_path)
