import json
import os
from arc_tools import logger
from arc_tools.grid import Color, Grid, SubGrid, copy_object, detect_objects, rotate_object, GridRegion, GridPoint, flip_horizontally, move_object, place_object, rotate_object_counter_clockwise
from arc_tools.plot import plot_grid, plot_grids
import numpy as np
# logger.setLevel(10)


def remove_consecutive_duplicates(data):
    output = [data[0]]
    for i in range(1,len(data)):
        if data[i] != data[i-1]:
            output.append(data[i])
    return output

def squeeze(grid: Grid):
    """ 
    change inner objects to single dots.
    """
    # Create a copy of the grid to avoid modifying the original
    
    # Detect all objects in the grid
    objects = detect_objects(grid)
    # plot_grids(objects, show=True)
    # Process each object
    first_obj_x = None
    first_obj_y = None
    new_dot_positions = []
    primary_color = grid.get_max_color()
    for obj in objects:
        # Check if object has no holes
        if not obj.has_hollow_space():
            # Get object color
            grid.remove_object(obj)
            
            # Place a single dot at the center of where the object was
            last_dot_x = obj.region.x2
            last_dot_y = obj.region.y2
            if first_obj_x is None:
                first_obj_x = last_dot_x
                first_obj_y = last_dot_y
            else:
                # logger.info(f"center_x: {center_x}, first_obj_x: {first_obj_x}")
                if last_dot_x != first_obj_x and obj.region.x1 <= first_obj_x <= obj.region.x2:
                    last_dot_x = first_obj_x
                if last_dot_y != first_obj_y and obj.region.y1 <= first_obj_y <= obj.region.y2:
                    last_dot_y = first_obj_y
            new_dot_positions.append((last_dot_x, last_dot_y))
            grid[last_dot_y][last_dot_x] = primary_color
    
    result = grid.get_frame()
    # find the key dot position that has dots on horizontal and vertical 
    for i,dot_position in enumerate(new_dot_positions):
        remaining_dot_positions = [dot_position1 for j,dot_position1 in enumerate(new_dot_positions) if j != i]
        if any(dot_position[0] == dot_position1[0] for dot_position1 in remaining_dot_positions) and any(dot_position[1] == dot_position1[1] for dot_position1 in remaining_dot_positions):
            key_dot_position = dot_position
            logger.info(f"key_dot_position: {key_dot_position}")
            logger.info(f"remaining_dot_positions: {remaining_dot_positions}")
            break
    else:
        key_dot_position = new_dot_positions[0]
    # place first dot
    def draw_border(horizontal_position, vertical_position):
        length = max(horizontal_position, vertical_position)
        w = 0
        h = 0
        w1 = 0
        h1 = 0
        for i in range(2, length, 2):
            w += 2
            h += 2
            w1 += 2
            h1 += 2
            # logger.info(f"w: {w}, h: {h}, horizontal_position: {horizontal_position}, vertical_position: {vertical_position}")
            if w1 == horizontal_position:
                w1 += 2
            if h1 == vertical_position:
                h1 += 2
            # top border
            for j in range(key_dot_position[0]-w, key_dot_position[0]+w+1):
                result[key_dot_position[1]-h][j] = primary_color
            # bottom border
            for j in range(key_dot_position[0]-w, key_dot_position[0]+w+1):
                result[key_dot_position[1]+h1][j] = primary_color
            # left border
            for j in range(key_dot_position[1]-h, key_dot_position[1]+h1+1):
                result[j][key_dot_position[0]-w] = primary_color
            # right border
            for j in range(key_dot_position[1]-h, key_dot_position[1]+h1+1):
                result[j][key_dot_position[0]+w1] = primary_color
            
    result[key_dot_position[1]][key_dot_position[0]] = primary_color
    data_dict = {'horizontal':3, 'vertical':3}
    for dot_position in remaining_dot_positions:
        if dot_position[1] == key_dot_position[1]:
            # horizontal
            data = grid[dot_position[1]][key_dot_position[0]:dot_position[0]+1]
            data = remove_consecutive_duplicates(data)
            # place the dots
            result[dot_position[1]][key_dot_position[0]+len(data)-1] = primary_color
            data_dict['horizontal'] = len(data)
        else:
            # vertical
            data = [grid[i][dot_position[0]] for i in range(key_dot_position[1],dot_position[1]+1)]
            data = remove_consecutive_duplicates(data)
            # place the dots
            result[key_dot_position[1]+len(data)-1][dot_position[0]] = primary_color
            data_dict['vertical'] = len(data)
    draw_border(data_dict['horizontal'] - 1, data_dict['vertical'] - 1)
    x1 = key_dot_position[0] - data_dict['horizontal'] + 3
    y1 = key_dot_position[1] - data_dict['vertical'] + 1
    x2 = x1 + data_dict['horizontal'] + 4
    y2 = y1 + data_dict['vertical'] + 5
    region = GridRegion([GridPoint(x1, y1), GridPoint(x2, y2)])
    logger.info(data_dict)
    logger.info(region)
    result = result.crop(region)
    plot_grid(result, show=True)
    return result
    

if __name__ == "__main__":
    # Set up environment
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 2d0172a1 squeeze")