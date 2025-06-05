from collections import Counter
from arc_tools import grid
from arc_tools.grid import Grid, detect_objects, Color, SubGrid, GridRegion, GridPoint, move_object
from arc_tools.plot import plot_grid, plot_grids
from arc_tools.logger import logger

def glue_it(grid: Grid) -> Grid:
    '''
    background color is blue
    two yellow objects with orange patches
    glue it by placing the second patch on top of the first patch
    '''
    
    # Detect yellow objects (color 1)
    grid.background_color = Color.BLUE.value
    yellow_objs = detect_objects(grid)

    # Sort objects by area (largest first, usually the first is the "base")
    yellow_objs = sorted(yellow_objs, key=lambda obj: obj.height * obj.width, reverse=True)
    obj1, obj2 = yellow_objs[0], yellow_objs[1]

    # Get orange patch positions in the second object (color 7)
    orange_pos_obj1 = obj1.get_position_of_dot(Color.ORANGE.value)[0]
    orange_pos_obj2 = [x for x in obj2.get_position_of_dot(Color.ORANGE.value) if x != orange_pos_obj1][0]
    # plot_grids([obj1, obj2], show=1)
    # remove the orange patch from the second object
    obj2.replace_color(Color.ORANGE.value, obj1.background_color)

    move_object(obj2, orange_pos_obj1.x - orange_pos_obj2.x, orange_pos_obj1.y - orange_pos_obj2.y - 1, grid, extend_grid=True)
    grid = detect_objects(grid)[0]
    return grid

if __name__ == "__main__":
    import os
    os.system("main.py 20270e3b glue_it")