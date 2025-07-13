import json
from math import ceil
import os
from collections import deque
from arc_tools import logger
from arc_tools.constants import EIGHT_DIRECTIONS
from arc_tools.grid import Color, Grid, SubGrid, copy_object, detect_objects, GridRegion, GridPoint, flip_horizontally, move_object, place_object
from arc_tools.plot import plot_grid, plot_grids

# logger.setLevel(10)

def fill_holes(grid: Grid):
    """
    Fill holes in the base object based on the reference object.
    """
    objects = detect_objects(grid)
    color_count = {obj.get_total_dots(): obj for obj in objects}
    ref_obj = color_count[max(color_count.keys())]
    base_obj = color_count[min(color_count.keys())]
    obj_color = base_obj.get_max_color()
    ref_grid = ref_obj.replace_color(obj_color, grid.background_color).get_full_grid()
    small_ref_obj = detect_objects(ref_grid,  go_diagonal=False,)
    result = Grid(base_obj.get_subgrid(safe=False))
    result.background_color = grid.background_color
    objects = detect_objects(result)
    max_size_obj = max(objects, key=lambda obj: obj.get_total_dots())
    for obj in objects:
        if obj != max_size_obj:
            result.remove_object(obj)
    old_background_color = base_obj.background_color
    result.background_color = obj_color
    small_base_obj = detect_objects(result,  required_color=Color(old_background_color), go_diagonal=False, ignore_corners=True)
    
    # Match objects based on their relative positions within their respective grids
    def get_relative_position(obj, grid_width, grid_height):
        center_x = (obj.region.x1 + obj.region.x2) / 2
        center_y = (obj.region.y1 + obj.region.y2) / 2
        # Normalize to relative position (0-1 range)
        rel_x = center_x / grid_width
        rel_y = center_y / grid_height
        return (rel_x, rel_y)
    
    # Get relative positions for both sets of objects
    base_positions = [(obj, get_relative_position(obj, result.width, result.height)) for obj in small_base_obj]
    ref_positions = [(obj, get_relative_position(obj, ref_grid.width, ref_grid.height)) for obj in small_ref_obj]
    
    # Sort by relative position (y first, then x for reading order)
    base_positions.sort(key=lambda x: (x[1][1], x[1][0]))
    ref_positions.sort(key=lambda x: (x[1][1], x[1][0]))
    
    # Extract sorted objects
    sorted_base_obj = [pos[0] for pos in base_positions]
    sorted_ref_obj = [pos[0] for pos in ref_positions]
    
    for obj, ref_obj in zip(sorted_base_obj, sorted_ref_obj):
        obj.replace_color(obj.get_max_color(), ref_obj.get_max_color(), in_place=True)
    return result

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 3a25b0d8 fill_holes")
    
