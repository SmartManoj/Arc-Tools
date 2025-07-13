import json
import os
from arc_tools import logger
from arc_tools.grid import Color, Grid, SubGrid, copy_object, detect_objects, GridRegion, GridPoint, flip_horizontally, move_object, place_object
from arc_tools.plot import plot_grid, plot_grids
import numpy as np
# logger.setLevel(10)


def clean_the_room(grid: Grid):
    """ 
    multi color object is the shelf (no corner dots).
    place the objects on the shelf on correct side.
    remove unncessary objects.
    """
    # Detect all objects
    objects = detect_objects(grid)

    # Find the shelf
    for obj in objects:
        if obj.get_total_unique_dots() > 1:
            shelf = obj
            objects.remove(obj)
            break
    
    def cmp(obj, dots):
        if dots == 'bottom':
            data = obj[-1]
        elif dots == 'top':
            data = obj[0]
        elif dots == 'left':
            data = [obj[i][0] for i in range(obj.height)]
        elif dots == 'right':
            data = [obj[i][-1] for i in range(obj.height)]
        if len(data) %2 == 1:
            return False
        centre_point = len(data)//2
        centre_data = data[centre_point-1:centre_point+1]
        remaining_data = data[:centre_point-1] + data[centre_point+1:]
        return all((v == obj.color for v in centre_data)) and all((v == obj.background_color for v in remaining_data))
    # Place the objects on the shelf
    for obj in objects:
        grid.remove_object(obj)
        if shelf[0][1] == obj.color:  # Top side
            # Rotate to have only 2 dots on bottom
            while not cmp(obj, 'bottom'):
                obj = obj.rotate()
            vx = next(i for i, dot in enumerate(obj[-1]) if dot != grid.background_color) - 1
            place_object(obj, shelf.region.x1 - vx, shelf.region.y1 - obj.height, grid)
        elif shelf[1][-1] == obj.color:  # Right side
            # Rotate to have only 2 dots on left
            while not cmp(obj, 'left'):
                obj = obj.rotate()
            place_object(obj, shelf.region.x2 + 1, shelf.region.y1, grid, remove_object=False)
        elif shelf[1][0] == obj.color:  # Left side
            # Rotate to have only 2 dots on right
            while not cmp(obj, 'right'):
                obj = obj.rotate()
            place_object(obj, shelf.region.x1 - obj.width, shelf.region.y1, grid, remove_object=False)
        elif shelf[-1][1] == obj.color:  # Bottom side
            # Rotate to have only 2 dots on top
            while not cmp(obj, 'top'):
                obj = obj.rotate()
            vx = next(i for i, dot in enumerate(obj[0]) if dot != grid.background_color) - 1
            place_object(obj, shelf.region.x1 - vx, shelf.region.y2 + 1, grid)
    
    # plot_grids([grid], show=True)
    return grid
    

if __name__ == "__main__":
    # Set up environment
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 2c181942 clean_the_room")