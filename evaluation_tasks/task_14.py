from collections import Counter
from arc_tools.grid import Grid, copy_object, detect_objects, Color, SubGrid, GridRegion, GridPoint, move_object
from arc_tools.plot import plot_grid, plot_grids
from arc_tools.logger import logger
import math

def shooting_lines(grid: Grid) -> Grid:
    '''
    bottom yellow line indicate the region.
    lines (4x1) (yellow, green, yellow) are falling down with 1 line gap.
    if green lines, the whole dots in the line will be green.
    '''
    obj = detect_objects(grid, required_color=Color.YELLOW)[0]
    x1, x2 = obj.region.x1, obj.region.x2
    y1, y2 = obj.region.y1, obj.region.y2
    if y1 == y2:
        # horizontal line
        for y in list(reversed(range(obj.region.y1))) + list(range(obj.region.y1, grid.height)):
            match abs(obj.region.y1 - y)%6:
                case 2 | 0:
                    color = Color.YELLOW.value
                case 4:
                    color = Color.GREEN.value
                case _:
                    color = grid.background_color
            for x in range(x1, x2+1):
                grid[y][x] = color
                if color == Color.GREEN.value:
                    for x in range(grid.width):
                        if grid[y][x] != grid.background_color:
                            grid[y][x] = Color.GREEN.value
    else:
        # vertical line
        for x in list(reversed(range(obj.region.x1))) + list(range(obj.region.x1, grid.width)):
            match abs(obj.region.x1 - x)%6:
                case 2 | 0:
                    color = Color.YELLOW.value
                case 4:
                    color = Color.GREEN.value
                case _:
                    color = grid.background_color
            for y in range(y1, y2+1):
                grid[y][x] = color
                if color == Color.GREEN.value:
                    for y in range(grid.height):
                        if grid[y][x] != grid.background_color:
                            grid[y][x] = Color.GREEN.value
    # plot_grids([grid], save_all=1, show=True)
    return grid

if __name__ == "__main__":
    import os
    os.system("main.py 221dfab4 shooting_lines")