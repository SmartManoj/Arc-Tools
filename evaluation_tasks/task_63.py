import os
from shutil import ReadError
from typing import Counter

from numpy import require
from arc_tools.grid import Grid, Square, copy_object, detect_objects, move_object
from arc_tools import logger
from arc_tools.plot import plot_grids

def water_tanks(grid: Grid):
    '''
    Water tanks transformation: Square boxes are water tanks that expand and fill pipes with majority color.
    - pipes get filled with the majority color from adjacent areas
    - center tank 3*3 (pipe color) is filled with majority surrounding color
    '''
    background_color = grid.background_color
    # adjacent color is the pipe color
    pipe_color = None
    for row in range(1, grid.height-1):
        for col in range(1, grid.width-1):
            if grid[row][col] == background_color:
                surrounding_colors = [grid[row-1][col], grid[row+1][col], grid[row][col-1], grid[row][col+1]]
                # if any is not background_color, then it is pipe color
                if any(_ := list(filter(lambda color: color != background_color, surrounding_colors))):
                    pipe_color = _[0]
                    break
        if pipe_color:
            break
    center_tank = detect_objects(grid, required_object=Square(3), required_color=pipe_color)[0]
    # remove it temporarily
    grid = grid.remove_object(center_tank)

    tanks = detect_objects(grid, go_diagonal=0)
    max_colors = []
    for tank in tanks:
        # find max color and replace pipe color with it
        max_color = list(filter(lambda color: color != pipe_color, tank.get_unique_values()))[0]
        tank.replace_color(pipe_color, max_color)
        max_colors.append(max_color)
    
    surrounding_points = center_tank.region.get_surrounding_points()
    data = [grid[y][x] for x, y in surrounding_points]
    overall_max_color = max(list(filter(lambda color: color != background_color, data)))
    # place at the center tank
    center_tank[1][1] = overall_max_color
    copy_object(center_tank, 0, 0, grid)


    
    return grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 800d221b water_tanks") 
