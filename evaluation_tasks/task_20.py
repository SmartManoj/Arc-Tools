import json
from arc_tools import logger
from arc_tools.grid import Color, Grid, SubGrid, copy_object, detect_objects, GridRegion, GridPoint, flip_horizontally, move_object, place_object
from arc_tools.plot import plot_grid, plot_grids
import numpy as np
# logger.setLevel(10)

def is_movable_down(grid: Grid, x: int, y: int):
    # go right and check if down path is clear
    for x1 in range(x+1, grid.width):
        if grid[y][x1] != Color.LIGHTBLUE.value:
            if grid[y+1][x1 - 1] == Color.LIGHTBLUE.value:
                return True
            return False
    # go left and check if down path is clear
    for x1 in reversed(range(x)):
        if grid[y][x1] != Color.LIGHTBLUE.value:
            if grid[y+1][x1 + 1] == Color.LIGHTBLUE.value:
                return True
            return False
    return False

def move_green_dot_down(grid: Grid, x: int, y: int):
    """Move a green dot down through light blue pipes"""
    visited = set()  # Track visited positions
    for i in range(100):
        # Try to move down
        if grid[y+1][x] == Color.LIGHTBLUE.value and (x, y+1) not in visited:
            visited.add((x, y))
            y += 1
        # Try to move right
        elif x < grid.width - 1 and grid[y][x+1] == Color.LIGHTBLUE.value and (x+1, y) not in visited:
            visited.add((x, y))
            x += 1
        # Try to move left
        elif x > 0 and grid[y][x-1] == Color.LIGHTBLUE.value and (x-1, y) not in visited:
            visited.add((x, y))
            x -= 1
        else:
            break  # No valid moves left
        if grid[y][x] == Color.GREEN.value:
            break
    grid[y][x] = Color.GREEN.value

def open_gatewall(grid: Grid):
    """ 
    pipe color - lightblue color
    gatewall - off state (three orange dots - horizontal);
    gatewall - on state (three magenta dots - vertical);
    green dots at corner should flow down.
    """
    # First convert orange dots to magenta dots
    for y in range(grid.height):
        for x in range(grid.width):
            if grid[y][x] == Color.ORANGE.value:
                # Convert horizontal orange dots to vertical magenta dots
                grid[y][x] = Color.LIGHTBLUE.value
                grid[y][x+2] = Color.LIGHTBLUE.value
                grid[y-1][x+1] = Color.MAGENTA.value
                grid[y][x+1] = Color.MAGENTA.value
                grid[y+1][x+1] = Color.MAGENTA.value
    
    # Then make green dots flow down
    for y in range(grid.height):
        for x in range(grid.width):
            if grid[y][x] == Color.GREEN.value and is_movable_down(grid, x, y):
                grid[y][x] = Color.LIGHTBLUE.value
                move_green_dot_down(grid, x, y)

    return grid

if __name__ == "__main__":
    import os
    os.environ['initial_file'] = __file__.split('.')[0]
    os.system("python main.py 2b83f449 open_gatewall")