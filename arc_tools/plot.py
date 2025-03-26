import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


def plot_grid(grid, name="grid.png"):
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
    # Remove ticks
    ax.set_xticks([])
    ax.set_yticks([])

    background_color = 'black'
    border_color = 'white'
    plt.savefig(name, facecolor=background_color, edgecolor=border_color)
    return ax

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
