import os

from matplotlib import widgets
from arc_tools.grid import Grid, detect_objects, Color, place_object_on_new_grid
from arc_tools import logger
from arc_tools.plot import plot_grids

def shape_smith(grid: Grid):
    '''
    """
    Constructs a new grid by repeating a detected shape object either vertically or horizontally, based on the input grid's aspect ratio. 
    Blue line is the divider.
    """
    '''
    objects = detect_objects(grid, ignore_colors=[Color.BLUE])
    is_vertical = grid.width < grid.height
    if not is_vertical:
        # sort by x
        objects.sort(key=lambda x: x.points[0].x)
    shape, *count_hints, shape_color_hint, background_color_hint = objects
    count = len(count_hints)
    # plot_grids([shape, shape_color_hint, background_color_hint])
    if is_vertical:
        height = (shape.height + 1) * count - 1
        width = shape.width
    else:
        height = shape.height
        width = (shape.width + 1) * count - 1
    output_grid = Grid([[background_color_hint.color for _ in range(width)] for _ in range(height)])
    shape  = shape.replace_all_color(shape_color_hint.color)
    for i in range(count):
        if is_vertical:
            place_object_on_new_grid(shape, 0, i * (shape.height + 1), output_grid)
        else:
            place_object_on_new_grid(shape, i * (shape.width + 1), 0, output_grid)
    return output_grid



    return grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py b0039139 shape_smith") 
