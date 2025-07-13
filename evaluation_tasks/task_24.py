import json
from math import ceil
import os
from arc_tools import logger
from arc_tools.grid import Color, Grid, SubGrid, copy_object, detect_objects, GridRegion, GridPoint, flip_horizontally, move_object, place_object
from arc_tools.plot import plot_grid, plot_grids
import numpy as np
# logger.setLevel(10)
def change_object_length(obj: SubGrid, length: int):
    """
    change the object length to the given length.
    """
    background_color = obj.parent_grid.background_color
    grid = obj.parent_grid
    if obj.height > length:
        # crop in both ends
        extra = ceil((obj.height - length) / 2)
        for i in range(extra):
            for j in range(obj.width):
                grid[obj.region.y1 + i][obj.region.x1 + j] = background_color
        for i in range(obj.height - length - extra):
            for j in range(obj.width):
                grid[obj.region.y2 - i][obj.region.x1 + j] = background_color
    elif obj.height < length:
        # add extra rows in both ends
        extra = ceil((length - obj.height) / 2)
        for i in range(extra):
            for j in range(obj.width):
                grid[obj.region.y1 - i - 1][obj.region.x1 + j] = obj.color
        for i in range(length - obj.height - extra):
            for j in range(obj.width):
                grid[obj.region.y2 + i + 1][obj.region.x1 + j] = obj.color

def ascend(grid: Grid):
    """ 
    change the object length in ascending order.
    magenta is the horizontal line.
    """
    objects = detect_objects(grid, single_color_only=True, ignore_color=Color.MAGENTA)
    # sort horizontally
    objects.sort(key=lambda x: x.region.x1)
    lengths = [obj.height for obj in objects]
    lengths.sort()
    # len of objects
    for obj, length in zip(objects, lengths):
        if obj.height != length:
            change_object_length(obj, length)

    return grid


if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 31f7f899 ascend")