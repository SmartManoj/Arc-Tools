import json
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from arc_tools.logger import logger

def plot_grid(grid: 'Grid', name="grid.png", show=False, close=True, ax=None):
    if not grid:
        logger.debug(f"Grid is empty")
        # breakpoint()
        return
    # Define colors
    colors = {
    0: 'black',
    1: 'blue',
    2: 'red',
    3: 'green',
    4: 'yellow',
    5: 'gray',
    6: 'purple',
    7: 'orange',
    8: 'lightblue',
    9: 'brown',

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
    ax.patch.set_edgecolor('red')  
    ax.patch.set_linewidth(2)  

    ax.imshow(grid, cmap=cmap, norm=norm)

    # Get grid dimensions
    height, width = np.array(grid).shape

    # Set major ticks for grid lines
    ax.set_xticks(np.arange(-.5, width, 1), minor=True)
    ax.set_yticks(np.arange(-.5, height, 1), minor=True)

    # Set ticks and labels for numbering
    ax.set_xticks(np.arange(0, width, 1))
    ax.set_yticks(np.arange(0, height, 1))
    ax.set_xticklabels(np.arange(0, width, 1))
    ax.set_yticklabels(np.arange(0, height, 1))

    # Add grid lines
    ax.grid(which='minor', color='#555555', linestyle='-', linewidth=1,  )

    # Customize tick parameters
    # ax.tick_params(axis='both', which='major', length=0) # Hide major tick lines - Removed to show ticks
    # ax.tick_params(axis='both', which='minor', length=0) # Hide minor tick lines - Removed to show ticks

    background_color = 'black'
    border_color = 'white'
    plt.savefig(name, facecolor=background_color, edgecolor=border_color)
    plt.title(name)
    def format_coord(x, y):
        if x >= -0.5 and y >= -0.5:
            col = int(x + 0.5)
            row = int(y + 0.5)
            return f'(x,y) = ({col},{row})'
        return ''

    ax.format_coord = format_coord
    if show:
        # Function to format coordinates
        print(f'Showing interactive plot for {name}...')
        plt.show(block=1)
    if close:
        plt.close()

def plot_grids(grids, name="grids.png", show=False):
    # plot the grids in a single plot
    fig, axs = plt.subplots(1, len(grids), figsize=(10, 5 * len(grids)))
    for i, grid in enumerate(grids):
        ax = plot_grid(grid, ax=axs[i] if len(grids) > 1 else axs, close=False)
        # axs[i].imshow(grid)
    plt.tight_layout()
    if show:
        plt.show(block=1)
    plt.savefig(name)
    plt.close()


if __name__ == "__main__":
    from arc_tools.grid import Grid
    from arc_tools.grid import find_square_boxes

    # data = json.load(open("grid.json", "r"))
    data = [[0,1]]
    grid = Grid(data)
    # find square boxes
    plot_grids([grid], name="input.png", show=0)
