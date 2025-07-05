import json
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from arc_tools.logger import logger
from glob import glob
import os

def remove_pngs():
    for file in glob('evaluation_tasks/*.png'):
        os.remove(file)

plot_grid_count = 0
disable_show = os.environ.get("DISABLE_SHOW", "0").lower() in ["true", "1"]
is_agent_terminal = os.environ.get("IS_AGENT_TERMINAL", "0").lower() in ["true", "1"]


def plot_grid(grid: 'Grid', name="grid.png", show=0, close=True, ax=None, save=True, save_all=False, title=None):
    global plot_grid_count
    if name == "grid.png" and save_all:
        plot_grid_count += 1
        name = f"grid_{plot_grid_count}.png"
    if not grid:
        logger.debug(f"Grid is empty")
        return
    # Define colors
    colors = {
    0: 'black',
    1: 'blue',
    2: 'red',
    3: 'green',
    4: 'yellow',
    5: 'lightgray',
    6: 'magenta',
    7: 'orange',
    8: 'lightblue',
    9: 'maroon',

    }
    norm = mcolors.BoundaryNorm(boundaries=range(len(colors)+1), ncolors=len(colors))

    # Create a colormap
    cmap = mcolors.ListedColormap([colors[i] for i in sorted(colors.keys())])
    cmap = mcolors.ListedColormap(
    ['#000000', '#0074D9','#FF4136','#2ECC40','#FFDC00',
     '#AAAAAA', '#F012BE', '#FF851B', '#7FDBFF', '#870C25'])

    # Plot
    if ax is None:
        fig, ax = plt.subplots()
    ax.patch.set_facecolor('black')  # Set plot background to black

    ax.imshow(grid, cmap=cmap, norm=norm)

    # Get grid dimensions
    height, width = np.array(grid).shape

    # Set major ticks for grid lines
    ax.set_xticks(np.arange(-.5, width, 1), minor=True)
    ax.set_yticks(np.arange(-.5, height, 1), minor=True)

    # Set ticks and labels for numbering
    ax.set_xticks(np.arange(0, width, 1))
    ax.set_yticks(np.arange(0, height, 1))
    ax.set_xticklabels(np.arange(0, width, 1), color='white')
    ax.set_yticklabels(np.arange(0, height, 1), color='white')

     # Add grid lines
    ax.grid(which='minor', color='#555555', linestyle='-', linewidth=1,  )
    
    # Customize tick parameters
    # ax.tick_params(axis='both', which='major', length=0) # Hide major tick lines - Removed to show ticks
    # ax.tick_params(axis='both', which='minor', length=0) # Hide minor tick lines - Removed to show ticks

    if ax is not None:
        ax.set_title(title or name, color='white', fontsize=12, pad=10)
    else:
        plt.title(title or name, color='white', fontsize=12, pad=10)
    if save:
        name = f'evaluation_tasks/{os.environ.get("initial_file", "main")}_{name}'
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
def plot_grids(grids, name="grids.png", show=1, save_all=False, title=None, titles=None):
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
        current_title = titles[i] if titles and len(titles) > i else title
        current_ax = axs[i]
        plot_grid(grid, ax=current_ax, close=False, save=False, title=current_title)
    
    # Ensure proper layout with titles and axes
    plt.tight_layout(pad=2.0)
    
    # Save before showing
    if name == "grids.png" and save_all:
        plot_grids_count += 1
        name = f"grids_{plot_grids_count}.png"
    name = f'evaluation_tasks/{os.environ.get("initial_file", "main")}_{name}'
    plt.savefig(name, facecolor='black', edgecolor='white', dpi=150, bbox_inches='tight', pad_inches=0.2)
    
    if show and not disable_show and not is_agent_terminal:
        plt.show(block=1)
    plt.close()


if __name__ == "__main__":
    from arc_tools.grid import Grid

    # data = json.load(open("grid.json", "r"))
    data = [[1,2,3],[2,1,4],[3,4,1]]
    grid = Grid(data)
    # find square boxes
    plot_grids([grid, grid], name="arc_tools/plot.png", show=1)
