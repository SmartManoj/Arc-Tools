from collections import Counter
from arc_tools import grid
from arc_tools.grid import Grid, detect_objects, Color, SubGrid, GridRegion, GridPoint, move_object, Square
from arc_tools.plot import plot_grid, plot_grids
from arc_tools.logger import logger

plus_pos = (-1,1),(0,1),(1,1),(0,2)

def is_plus(x,y,grid):
    for dx,dy in plus_pos:
        if grid[y+dy][x+dx] != Color.YELLOW.value:
            return False
    return True

def highlight_plus(grid: Grid) -> Grid:
    '''
    replace yellow plus with light blue plus
    '''
    for y in range(grid.height):
        for x in range(grid.width):
            if grid[y][x] == Color.YELLOW.value:
                if is_plus(x,y,grid):
                    grid[y][x] = Color.LIGHTBLUE.value
                    for dx,dy in plus_pos:
                        grid[y+dy][x+dx] = Color.LIGHTBLUE.value
    return grid

if __name__ == "__main__":
    import os
    os.system("python main.py 1818057f highlight_plus")