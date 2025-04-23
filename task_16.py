import json
from arc_tools.grid import Grid, rotate_object, GridRegion, GridPoint, flip_horizontally

def check_subgrid(grid: Grid, full_grid: Grid) -> bool:
    for big_row in range(full_grid.height - grid.height + 1):
        for big_col in range(full_grid.width - grid.width + 1):
            subgrid = full_grid.crop(GridRegion([GridPoint(big_col, big_row), GridPoint(big_col + grid.width - 1, big_row + grid.height - 1)]))
            if subgrid == grid:
                return True
    return False

def extrapolation(grid: Grid) -> Grid:
    """ 
    reference_output is the output of the first train task
    change reference output's color according to grid's color
    extrapolate the grid using reference output (rotate and mirror if needed).
    """
    with open('reference_output.json', 'r') as f:
        full_grid = Grid(json.load(f))
    
    full_grid.replace_color(full_grid.get_max_color(), -1)
    full_grid.replace_color(full_grid.background_color, grid.background_color)
    full_grid.replace_color(-1, grid.get_max_color())

    for _ in range(8):
        if check_subgrid(grid, full_grid):
            return full_grid
        full_grid = rotate_object(full_grid)
        if _ == 3:
            full_grid = flip_horizontally(full_grid)
        
    assert False, "No match found"

if __name__ == "__main__":
    import os
    os.system("main.py 269e22fb extrapolation")