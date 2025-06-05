import json
from math import ceil
import os
from collections import deque
from arc_tools import logger
from arc_tools.constants import EIGHT_DIRECTIONS
from arc_tools.grid import Color, Grid, SubGrid, copy_object, detect_objects, rotate_object, GridRegion, GridPoint, flip_horizontally, move_object, place_object, rotate_object_counter_clockwise
from arc_tools.plot import plot_grid, plot_grids

# logger.setLevel(10)

def shoot(grid: Grid):
    '''
    shoot from the center of the object; bullet will be placed 5 dots away from the center
    objects = half-y, L tetromino
    bullet color = maroon
    double bullet = blue
    '''
    result = grid
    
    # Detecqt all objects in the grid
    objects = detect_objects(grid)
    # Process each object to find shooting objects (L-shaped or half-y tetrominos)
    for obj in objects:
        # detect shape
        if obj.height == 2 and obj.width == 2:
            obj_name = 'l-triomino'
        elif obj.height * obj.width == 6:
            obj_name = 'half-y'
        else:
            logger.info(f'unknown object: {obj.height}x{obj.width}')
            plot_grid(obj, show=1)
            continue
        
        
        # get center position
        if obj_name == 'l-triomino':
            # find the empty dot
            found = False
            for y in range(obj.height):
                for x in range(obj.width):
                    if obj.get(x, y) == obj.background_color:
                        empty_x = x
                        empty_y = y
                        found = True
                        break
                if found:
                    break
            if (empty_x, empty_y) == (0, 0):
                direction = (1, 1)
            elif (empty_x, empty_y) == (1, 0):
                direction = (-1, 1)
            elif (empty_x, empty_y) == (0, 1):
                direction = (1, -1)
            elif (empty_x, empty_y) == (1, 1):
                direction = (-1, -1)
            gun_x = obj.region.x1 + empty_x + direction[0]
            gun_y = obj.region.y1 + empty_y + direction[1]
        elif obj_name == 'half-y':
            # find the empty dot
            # up
            if obj.width == 3 and obj[0][1] == obj.color:
                direction = (0, -1)
                tip = (1, 0)
            # down
            elif obj.width == 3 and obj[1][1] == obj.color:
                direction = (0, 1)
                tip = (1, 1)
            # left
            elif obj.width == 2 and obj[1][0] == obj.color:
                direction = (-1, 0)
                tip = (0, 1)
            elif obj.width == 2 and obj[1][1] == obj.color:
                direction = (1, 0)
                tip = (1, 1)
            gun_x = obj.region.x1 + tip[0]
            gun_y = obj.region.y1 + tip[1]
        
        # shoot
        bullet_x = gun_x + (direction[0] * 5)
        bullet_y = gun_y + (direction[1] * 5)
        if result.get(bullet_x, bullet_y) == result.background_color:
            result.set(bullet_x, bullet_y, Color.MAROON.value)
        elif result.get(bullet_x, bullet_y) == Color.MAROON.value:
            result.set(bullet_x, bullet_y, Color.BLUE.value)
        else:
            # detect object at x, y and replace with Maroon
            obj = detect_objects(result, point = GridPoint(bullet_x, bullet_y))[0]
            obj.replace_color(obj.color, Color.MAROON.value, in_place=True)

    
    return result

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 409aa875 shoot")
    
