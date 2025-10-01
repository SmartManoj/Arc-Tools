from ast import main
import os
from arc_tools.grid import Grid, detect_objects, Color, flip_vertically, place_object, place_object_on_new_grid
from arc_tools import logger
from arc_tools.plot import plot_grids

def role_model_v4(grid: Grid):
    '''
    Blue line divider - replicate the main object to all quadrants by flipping accordingly
    '''
    objects = detect_objects(grid)[1:]
    main_object, *objects = objects
    main_objects = detect_objects(main_object, single_color_only=1)
    
    # Find the main red object (reference object)
    main_red_object = None
    for idx, obj in enumerate(main_objects):
        if obj.color == Color.RED.value:
            main_red_object = main_objects.pop(idx)
            break
    for main_obj in main_objects:
        width_factor = main_obj.width / main_red_object.width
        height_factor = main_obj.height / main_red_object.height
        # check position - 8 directions
        dx = main_obj.region.x1 - main_red_object.region.x1 
        dy = main_obj.region.y1 - main_red_object.region.y1 
        
        for obj in objects:
            width_factor1 = obj.width / main_red_object.width
            height_factor1 = obj.height / main_red_object.height
            position = int(dx * width_factor1), int(dy * height_factor1)
            # if top right quadrant, flip x axis
            if obj.region.x1 > grid.width / 2 and obj.region.y1 < grid.height / 2:
                flip_vertically = False
                flip_horizontally = True
            elif obj.region.x1 < grid.width / 2 and obj.region.y1 > grid.height / 2:
                flip_vertically = True
                flip_horizontally = False
            elif obj.region.x1 > grid.width / 2 and obj.region.y1 > grid.height / 2:
                flip_vertically = True
                flip_horizontally = True
            new_obj_height = int(obj.height * height_factor)
            new_obj_width = int(obj.width * width_factor)
            for row in range(new_obj_height):
                for col in range(new_obj_width):
                    if flip_horizontally:
                        x = obj.region.x2 - position[0] - col
                    else:
                        x = obj.region.x1 + position[0] + col
                    if flip_vertically:
                        y = obj.region.y2 - position[1] - row
                    else:
                        y = obj.region.y1 + position[1] + row
                    grid[y][x] = main_obj.color


    return grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py b10624e5 role_model_v4") 
