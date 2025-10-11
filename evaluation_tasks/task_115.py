import os
from arc_tools.grid import Grid, detect_objects, Color, place_object, place_object_on_new_grid
from arc_tools import logger
from arc_tools.plot import plot_grids

def sculpt(grid: Grid):
    '''
    sculpt inside gray frame; use hint colors and shapes
    '''
    frame = detect_objects(grid, required_colors=[Color.GRAY])[0]
    result = grid.crop(frame.region)
    grid.remove_object(frame, clean_area=True)
    objects = detect_objects(grid)
    hint_colors = {}
    hint_shapes = {}
    for obj in objects:
        if len(obj.colors) == 2:
            hint_colors[obj[0][0]] = obj[0][obj.width-1]
        else:
            if obj.width == obj.height:
                hint_shapes[obj.color] = grid.crop(obj.region)
    objects = detect_objects(result, ignore_colors=[Color.GRAY])
    for obj in objects:
        result.remove_object(obj)
        new_obj = hint_shapes[obj.color]
        new_obj = new_obj.replace_color(obj.color, hint_colors[obj.color], replace_in_parent_grid=0)
        place_object_on_new_grid(new_obj, obj.region.x1, obj.region.y1, result)

    return result

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py edb79dae sculpt") 
