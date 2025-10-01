import os
from arc_tools.grid import Grid, detect_objects, Color, place_object_on_new_grid
from arc_tools import logger
from arc_tools.plot import plot_grids

def role_model_v5(grid: Grid):
    '''
    replicate object as hint_map (single color object)
    '''
    objects = detect_objects(grid)
    for obj in objects:
        if len(obj.colors) == 1:
            hint_map = obj
        else:
            replicate_obj = obj
    
    output_grid = Grid([[grid.background_color for _ in range(hint_map.width * replicate_obj.width)] for _ in range(hint_map.height * replicate_obj.height)])

    for row in range(hint_map.height):
        for col in range(hint_map.width):
            if hint_map[row][col] == hint_map.color:
                place_object_on_new_grid(replicate_obj, col * replicate_obj.width, row * replicate_obj.height,  output_grid)

    return output_grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py bf45cf4b role_model_v5") 
