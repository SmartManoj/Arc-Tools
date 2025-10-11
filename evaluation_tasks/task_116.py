import os
from arc_tools.grid import Grid, GridRegion, detect_objects, Color, place_object_on_new_grid
from arc_tools import logger
from arc_tools.plot import plot_grids

def join_the_forces(grid: Grid):
    '''
    Transform a 6x6 grid into a 16x16 grid with a tiled pattern.
    The non-background colored shape gets marked with color 9 in the center region.
    '''
    objects = detect_objects(grid)
    if len(objects) == 1:
        obj = objects[0]
    else:
        # crop the pattern
        obj = grid.crop(GridRegion([(objects[0].region.x1, objects[0].region.y1), (objects[-1].region.x2, objects[-1].region.y2)]))
    pattern = obj.replace_all_color(Color.MAROON)
    inverse_pattern = pattern.copy().replace_color(Color.MAROON, Color.BLACK, replace_in_parent_grid=False)
    inverse_pattern.background_color = Color.BLACK.value
    result = Grid([[Color.BLACK.value for _ in range(16)] for _ in range(16)])
    
    # place like this
    # 1 2
    # 3 4

    place_object_on_new_grid(pattern, result.center.x, result.center.y, result)
    place_object_on_new_grid(pattern, result.center.x - pattern.width, result.center.y, result)
    place_object_on_new_grid(pattern, result.center.x, result.center.y - pattern.height, result)
    place_object_on_new_grid(pattern, result.center.x - pattern.width, result.center.y - pattern.height, result)
    for x in range(-4, result.width, inverse_pattern.width):
        for y in range(-4, result.height, inverse_pattern.height):
            place_object_on_new_grid(inverse_pattern, x, y, result)
    
    
    return result

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py eee78d87 join_the_forces") 
