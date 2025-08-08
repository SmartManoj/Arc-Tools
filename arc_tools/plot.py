from matplotlib.backend_bases import MouseButton
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import pyperclip
from arc_tools.logger import logger
from glob import glob
import os
import math

def remove_pngs():
    for file in glob('evaluation_tasks/*.png'):
        os.remove(file)

plot_grid_count = 0
disable_show = os.environ.get("DISABLE_SHOW", "0").lower() in ["true", "1"]
is_agent_terminal = (os.environ.get("IS_AGENT_TERMINAL", '') or os.environ.get("COMPOSER_NO_INTERACTION", '').lower() in ["true", "1"])
IS_ARC_AGI_3 = True

def plot_grid(grid: 'Grid', name="grid.png", show=1, close=True, ax=None, save=True, save_all=False, title=None):
    global plot_grid_count
    if name == "grid.png" and save_all:
        plot_grid_count += 1
        name = f"grid_{plot_grid_count}.png"
    if not grid:
        logger.debug(f"Grid is empty")
        return
    # Define colors
    if IS_ARC_AGI_3:
        colors = ['#FFFFFF', '#CCCCCC', '#999999', '#666666', '#333333', '#000000', '#E53AA3', '#FF7BCC', '#F93C31', '#1E93FF', '#88D8F1', '#FFDC00', '#FF851B', '#921231', '#4FCC30', '#A356D6']
    else:
        colors = ['#000000', '#0074D9','#FF4136','#2ECC40','#FFDC00', '#AAAAAA', '#F012BE', '#FF851B', '#7FDBFF', '#870C25']
    norm = mcolors.BoundaryNorm(boundaries=range(len(colors)+1), ncolors=len(colors))

    # Create a colormap
    cmap = mcolors.ListedColormap(colors)

    # Plot
    if ax is None:
        fig, ax = plt.subplots()
        # Set window title (safe on environments without GUI manager)
        window_title = title or name
        manager = getattr(getattr(fig.canvas, 'manager', None), 'set_window_title', None)
        if callable(manager):
            manager(window_title)
    ax.patch.set_facecolor('black')  # Set plot background to black

    ax.imshow(grid, cmap=cmap, norm=norm)

    # Get grid dimensions
    height, width = np.array(grid).shape

    # Set major ticks for grid lines
    ax.set_xticks(np.arange(-.5, width, 1), minor=True)
    ax.set_yticks(np.arange(-.5, height, 1), minor=True)

    # Set ticks and labels for numbering with dynamic thinning to avoid collisions
    def _step(n: int, max_labels: int = 24) -> int:
        return max(1, int(math.ceil(n / max_labels)))

    x_step = _step(width)
    y_step = _step(height)

    x_ticks = np.arange(0, width, x_step)
    y_ticks = np.arange(0, height, y_step)

    ax.set_xticks(x_ticks)
    ax.set_yticks(y_ticks)
    ax.set_xticklabels([str(i) for i in x_ticks], color='white')
    ax.set_yticklabels([str(i) for i in y_ticks], color='white')
    ax.tick_params(axis='both', labelsize=8, top=False, right=False, labeltop=False)

     # Add grid lines
    ax.grid(which='minor', color='#4b4b4b', linestyle='-', linewidth=0.1)
    
    # Customize tick parameters
    # ax.tick_params(axis='both', which='major', length=0) # Hide major tick lines - Removed to show ticks
    # ax.tick_params(axis='both', which='minor', length=0) # Hide minor tick lines - Removed to show ticks

    if ax is not None:
        ax.set_title(title or name, color='white', fontsize=12, pad=10)
    else:
        plt.title(title or name, color='white', fontsize=12, pad=10)
    if save:
        initial_file = os.environ.get("initial_file")
        if initial_file:
            name = f'evaluation_tasks/{initial_file}_{name}'
        plt.savefig(name, facecolor='black', edgecolor='white', dpi=150, bbox_inches='tight', pad_inches=0.2)
    def format_coord(x, y):
        if x >= -0.5 and y >= -0.5:
            col = int(x + 0.5)
            row = int(y + 0.5)
            return f'(row,col) = ({row},{col})\t(x,y) = ({col},{row})'
        return ''

    ax.format_coord = format_coord
    if show and not disable_show and not is_agent_terminal:
        # Function to format coordinates
        print(f'Showing interactive plot for {name}...')
        plt.show(block=1)
    if close:
        plt.close()

plot_grids_count = 0
def plot_grids(grids, name=None, show=1, save_all=False, titles=None):
    if len(grids) == 0:
        print("No grids to plot")
        return
    global plot_grids_count
    # plot the grids in a single plot
    fig, axs = plt.subplots(1, len(grids), figsize=(10, 5 * len(grids)))
    fig.patch.set_facecolor('black')  # Set figure background to black
    
    
    if len(grids) == 1:
        axs = [axs]  # Make it iterable for single grid case
    for i, grid in enumerate(grids):
        current_title = titles[i] if titles and len(titles) > i else f'plot_{i+1}'
        current_ax = axs[i]
        plot_grid(grid, ax=current_ax, close=False, save=False, title=current_title, show=0)
    
    # Ensure proper layout with titles and axes
    plt.tight_layout(pad=2.0)
    
    # Save before showing
    if not name:
        name = "grids.png"
    if name == "grids.png" and save_all:
        plot_grids_count += 1
        name = f"grids_{plot_grids_count}.png"
    prefix = os.environ.get("initial_file", "main")
    name = f'{prefix}_{name}'
    # Set window title (safe on environments without GUI manager)
    manager = getattr(getattr(fig.canvas, 'manager', None), 'set_window_title', None)
    if callable(manager):
        manager(name)
    
    initial_file = os.environ.get("initial_file")
    if initial_file:
        name = f'evaluation_tasks/{name}'
    plt.savefig(name, facecolor='black', edgecolor='white', dpi=150, bbox_inches='tight', pad_inches=0.2)
    
    def on_click(event):
        if event.button is MouseButton.LEFT:
            if event.xdata and event.xdata >= -0.5 and event.ydata and event.ydata >= -0.5:
                col = int(event.xdata + 0.5)
                row = int(event.ydata + 0.5)
                copy_msg = f'(row,col) = ({row},{col})'
                pyperclip.copy(copy_msg)
    plt.connect('button_press_event', on_click)
    if show and not disable_show and not is_agent_terminal:
        plt.show(block=1)
    plt.close()


if __name__ == "__main__":
    from arc_tools.grid import Grid

    # data = json.load(open("grid.json", "r"))
    data = [[1,2,3],[2,1,4],[3,4,1]]
    grid = Grid(data)
    # find square boxes
    plot_grids([grid, grid], name="plot.png", show=1)
