import os
from arc_tools.grid import Grid, copy_object, detect_objects, place_object_on_new_grid
from arc_tools import logger
from arc_tools.plot import plot_grids

def role_model_v3(grid: Grid):
    '''
    role model = dot shape
    '''
    objects = detect_objects(grid)
    # sort by area
    objects.sort(key=lambda x: x.area, reverse=True)
    shape, dots = objects[0], objects[1:]
    # shape color is the main dot
    main_dot = [dot for dot in dots if dot.color == shape.color][0]

    cx, cy = main_dot.region.start
    for dot in dots:
        x,y = dot.region.start
        dx, dy = (x - cx) //2 * shape.width , (y - cy) // 2 * shape.height
        copy_object(shape, dx, dy, grid)
    shape.replace_all_color(dots[0].color, in_place=1)
    # remove all dots
    for dot in dots:
        grid.remove_object(dot)
    return grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py a395ee82 role_model_v3") 
