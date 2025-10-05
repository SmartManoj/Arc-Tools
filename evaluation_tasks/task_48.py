from collections import defaultdict
import os
from arc_tools.grid import Color, Grid, detect_objects, place_object_on_new_grid
from arc_tools import logger
from arc_tools.plot import plot_grids

def role_model(grid: Grid):
    '''
    first layer - shape
    second layer - output position based on color
    third layer - color of the result shape;
    last row indicates number of objects
    ---
    second layer dots will be changed to the shape of the first layer of its color (role model)
    the shape will get the last layer color
    grey color is the divider.
    '''
    objects = detect_objects(grid, ignore_color=Color.GRAY)
    for y in range(grid.height - 1, -1, -1):
        n_objects = len(set([grid.get(i, y) for i in range(grid.width) if grid.get(i, y) != grid.background_color]))
        if n_objects:
            break
    # first row, first divider pos 
    object_shape = next(i for i, v in enumerate(grid.get_top_side()) if v == Color.GRAY.value) 
    first_layer = objects[0:n_objects]
    second_layer = objects[n_objects:-n_objects]
    third_layer = objects[-n_objects:]
    shape_map = {o.color: o for o in first_layer}
    color_map = {f.color: t.color for f, t in zip(first_layer, third_layer)}
    pos_map_color = defaultdict(list)
    modulus_value = object_shape + 1
    for pos_map in second_layer:
        for x, y in pos_map.points:
            pos_map_color[pos_map.color].append((x%modulus_value, y%modulus_value))
    n_objects2 = object_shape * object_shape
    new_data = [[grid.background_color for _ in range(n_objects2)] for _ in range(n_objects2)]
    result_grid = Grid(new_data, background_color=Color.BLACK.value)
    for color, pos_list in pos_map_color.items():
        for pos in pos_list:
            place_object_on_new_grid(shape_map[color], pos[0] * object_shape, pos[1] * object_shape, result_grid, color_map.get(color, color))

    return result_grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 65b59efc role_model") 
