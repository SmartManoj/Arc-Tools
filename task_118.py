
from arc_tools.grid import Grid, GridPoint, GridRegion, SubGrid
from arc_tools.plot import plot_grid, plot_grids

def row_col_color_data(grid: Grid) -> Grid:
    """
    Create a new grid with row, col, and color data.

    Args:
        divide the grid into 4 subgrids and return the new grid with row, col, and background color (ratio map), data.
        
    """
    grid.background_color = 0
    grid_size = len(grid)
    subgrid_size = grid_size//2
    # plot_grid(grid, name="input.png", show=True)
    first_piece =  SubGrid(GridRegion([GridPoint(0, 0), GridPoint(subgrid_size-1, subgrid_size-1)]), grid)
    second_piece = SubGrid(GridRegion([GridPoint(subgrid_size, 0), GridPoint(2*subgrid_size-1, subgrid_size-1)]), grid)
    third_piece =  SubGrid(GridRegion([GridPoint(0, subgrid_size), GridPoint(subgrid_size-1, 2*subgrid_size-1)]), grid)
    fourth_piece = SubGrid(GridRegion([GridPoint(subgrid_size, subgrid_size), GridPoint(2*subgrid_size-1, 2*subgrid_size-1)]), grid)
    # plot_grids([first_piece, second_piece, third_piece, fourth_piece], show=1, save_all=True)
    rows = first_piece.get_total_dots()
    cols = second_piece.get_total_dots()
    new_grid = []
    row_ratio = rows//subgrid_size or 1
    col_ratio = cols//subgrid_size or 1
    for row in range(rows):
        new_row = []
        for col in range(cols):
            row_idx = row % subgrid_size
            col_idx = col % subgrid_size
            new_val = fourth_piece[row_idx][col_idx]
            if not new_val:
                new_val = third_piece[(row//row_ratio)%subgrid_size][(col//col_ratio)%subgrid_size]
            new_row.append(new_val)
        new_grid.append(new_row)
    return Grid(new_grid)

if __name__ == "__main__":
    import os
    os.system("main.py f931b4a8 row_col_color_data")


