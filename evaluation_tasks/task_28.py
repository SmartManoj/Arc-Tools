import json
from math import ceil
import os
from collections import deque
from arc_tools import logger
from arc_tools.constants import EIGHT_DIRECTIONS
from arc_tools.grid import Color, Grid, SubGrid, copy_object, detect_objects, GridRegion, GridPoint, flip_horizontally, move_object, place_object
from arc_tools.plot import plot_grid, plot_grids
import numpy as np

# logger.setLevel(10)

def unique_objects(grid: Grid):
    """
    Square box with color at cell (1, 1) is the object.
    background color is first dot.
    """
    # Find all unique objects in the grid
    grid.background_color = grid[0][0]
    objects = detect_objects(grid, required_color=Color(grid[1][1]))
    max_size = max(obj.height for obj in objects)
    # Find unique objects by comparing their patterns
    unique_objects = []
    for k, obj in enumerate(objects):
        is_unique = True
        if obj.height != max_size:
            continue
        for rem_obj in objects:
            if obj == rem_obj:
                continue
            if obj.compare(rem_obj):
                is_unique = False
                break
        if is_unique:
            unique_objects.append(obj)
    
    size_of_the_object = unique_objects[0].height
    new_grid = Grid([[grid.background_color for _ in range(size_of_the_object + 2)] for _ in range((size_of_the_object + 1) * len(unique_objects) + 1)])
    # stack the unique objects vertically
    for i, obj in enumerate(unique_objects):
        place_object(obj, 1, 1 + (size_of_the_object + 1) * i, new_grid)
    return new_grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 38007db0 unique_objects")
    
