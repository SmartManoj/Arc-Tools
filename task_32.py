import json
from math import ceil
import os
from collections import deque, Counter
from arc_tools import logger
from arc_tools.constants import EIGHT_DIRECTIONS
from arc_tools.grid import Color, Grid, SubGrid, copy_object, detect_objects, rotate_object, GridRegion, GridPoint, flip_horizontally, move_object, place_object, rotate_object_counter_clockwise, place_object_on_new_grid
from arc_tools.plot import plot_grid, plot_grids

logger.setLevel(10)
def remove_marker(obj: SubGrid, clue_piece_color: Color):
    # check topleft corner
    grid = obj.parent_grid
    x1, y1, x2, y2 = obj.region.x1, obj.region.y1, obj.region.x2, obj.region.y2
    if obj[0][0] == clue_piece_color:
        grid[y1][x1] = obj.background_color
        grid[y1][x1 + 1] = obj.background_color
        grid[y1 + 1][x1] = obj.background_color
        x1 += 1
        y1 += 1
        frame_color = grid[y1][x1]
        corner = 'top_left'
    # check topright corner
    if obj[0][obj.width - 1] == clue_piece_color:
        grid[y1][x2] = obj.background_color
        grid[y1][x2 - 1] = obj.background_color
        grid[y1 + 1][x2] = obj.background_color
        x2 -= 1
        y1 += 1
        frame_color = grid[y1][x2]
        corner = 'top_right'
    # check bottomleft corner
    if obj[obj.height - 1][0] == clue_piece_color:
        grid[y2][x1] = obj.background_color
        grid[y2][x1 + 1] = obj.background_color
        grid[y2 - 1][x1] = obj.background_color
        x1 += 1
        y2 -= 1
        frame_color = grid[y2][x1]
        corner = 'bottom_left'
    # check bottomright corner
    if obj[obj.height - 1][obj.width - 1] == clue_piece_color:
        grid[y2][x2] = obj.background_color
        grid[y2][x2 - 1] = obj.background_color
        grid[y2 - 1][x2] = obj.background_color
        x2 -= 1
        y2 -= 1
        frame_color = grid[y2][x2]
        corner = 'bottom_right'
    return SubGrid(GridRegion([GridPoint(x1, y1), GridPoint(x2, y2)]), grid), corner, frame_color

def join_the_frame(grid: Grid):
    '''
    1. First move object 2 to above object 4 and object 3 to left of object 4
    2. Connect all objects with orange color
    3. Remove the yellow color
    '''
    result = grid.get_frame()
    
    # Detect all objects in the grid
    objects = detect_objects(grid)
    # find the object with yellow color
    for obj in objects:
        corner_colors = set(obj.get_corner_colors())
        if len(corner_colors) > 2:
            static_object = obj
            clue_piece_color = (corner_colors - {obj.color, grid.background_color}).pop()
            logger.info(f"{clue_piece_color = } {obj.color = } {grid.background_color = }")
            break
    # plot_grid(static_object, "static_object.png", show=1)
    remaining_objects = [obj for obj in objects if obj != static_object]
    static_object, corner, frame_color = remove_marker(static_object, clue_piece_color)
    place_object_on_new_grid(static_object, static_object.region.x1, static_object.region.y1, result)
    if corner == 'top_left':
        # pick object having frame color in left side and add it below to this
        for obj in remaining_objects:
            if all(obj[row][0] == frame_color for row in range(obj.height)):
                new_x = static_object.region.x1
                new_y = static_object.region.y2 + 1
                place_object_on_new_grid(obj, new_x, new_y, result)
                break
        # pick object having frame color in top side and add it right to this
        static_top = static_object.region.y1
        for obj in remaining_objects:
            if all(obj[0][col] == frame_color for col in range(obj.width)):
                new_y = static_top
                new_x = static_object.region.x2 + 1
                place_object_on_new_grid(obj, new_x, new_y, result)
        # pick object having frame color in bottom side and add it left to this (bottom_left piece)
        for obj in remaining_objects:
            if all(obj[obj.height - 1][col] == frame_color for col in range(obj.width)):
                new_x = static_object.region.x2 + 1
                new_y = static_object.region.y2 + 1
                place_object_on_new_grid(obj, new_x, new_y, result)
                break
    elif corner == 'bottom_left':
        # pick object having frame color in left side and add it above to this
        for obj in remaining_objects:
            if all(obj[row][0] == frame_color for row in range(obj.height)):
                new_x = static_object.region.x1
                new_y = static_object.region.y1 - obj.height
                place_object_on_new_grid(obj, new_x, new_y, result)
                break
        # pick object having frame color in bottom side and add it right to this
        for obj in remaining_objects:
            if all(obj[obj.height - 1][col] == frame_color for col in range(obj.width)):
                new_x = static_object.region.x2 + 1
                new_y = static_object.region.y2 - (obj.height - 1)
                place_object_on_new_grid(obj, new_x, new_y, result)
                break
    elif corner == 'bottom_right':
        # pick object having frame color in right side and add it above to this
        for obj in remaining_objects:
            if all(obj[row][obj.width - 1] == frame_color for row in range(obj.height)):
                new_x = static_object.region.x2 - (obj.width - 1)
                new_y = static_object.region.y1 - obj.height
                place_object_on_new_grid(obj, new_x, new_y, result)
                break
        # pick object having frame color in bottom side and add it left to this
        static_left = static_object.region.x1
        for obj in remaining_objects:
            if all(obj[obj.height - 1][col] == frame_color for col in range(obj.width)):
                new_x = static_left - obj.width
                static_left = new_x
                new_y = static_object.region.y2 - (obj.height - 1)
                place_object_on_new_grid(obj, new_x, new_y, result)
    plot_grid(result, "static_object.png", show=1)


    return result

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 446ef5d2 join_the_frame")
    
