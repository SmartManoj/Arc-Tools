import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np


def plot_grid(grid, name="grid.png", show=False):
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

    # Plot
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
    ax.grid(which='minor', color='grey', linestyle='-', linewidth=0.5)

    # Customize tick parameters
    # ax.tick_params(axis='both', which='major', length=0) # Hide major tick lines - Removed to show ticks
    # ax.tick_params(axis='both', which='minor', length=0) # Hide minor tick lines - Removed to show ticks

    background_color = 'black'
    border_color = 'white'
    plt.savefig(name, facecolor=background_color, edgecolor=border_color)
    plt.title(name)
    if show:
        print('Showing')
        plt.show(block=True)
    plt.close()

def plot_grids(grids, name="grids.png"):
    fig, axs = plt.subplots(len(grids), 1, figsize=(10, 5 * len(grids)))
    for i, grid in enumerate(grids):
        ax = plot_grid(grid, ax=axs[i])
    plt.tight_layout()
    plt.show()
    background_color = 'black'
    border_color = 'white'
    plt.savefig(name, facecolor=background_color, edgecolor=border_color)


if __name__ == "__main__":
    grid = [
    [1,2,3,4,5,6,7,8,9],
    [0, 5, 5, 5, 0, 5, 5, 5, 0],
    [0, 5, 5, 5, 0, 5, 0, 5, 0],
    [0, 5, 5, 5, 0, 5, 5, 5, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
]
    a= [(9, 10), (9, 11), (10, 11), (9, 12), (11, 11), (10, 12), (9, 13), (11, 12), (11, 10), (10, 13), (12, 12), (11, 13), (10, 14)]
    m, n = 22, 22
    grid = [[0 for _ in range(n)] for _ in range(m)]
    for i, j in a:
        grid[i-1][j-1] = 1
    plot_grid(grid, name="actual_output3.png")
