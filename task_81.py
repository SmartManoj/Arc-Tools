from arc_tools import grid
from arc_tools.grid import Grid, detect_objects, Color, SubGrid, GridRegion, GridPoint, move_object, rotate_object
from arc_tools.plot import plot_grid, plot_grids
from itertools import combinations
from arc_tools.logger import logger
def merge_objects(objects: list[SubGrid]):
    new_objects = []
    remaining_objects = []
    for obj in objects:
        if obj.get_total_unique_dots() == 2:
            new_objects.append(obj)
        else:
            remaining_objects.append(obj)
    # Merge regions that share same x or y coordinates
    merged_objects = []
    while remaining_objects:
        current = remaining_objects.pop(0)
        merged = False
        for i, other in enumerate(remaining_objects):
            # Check if regions share same x or y coordinates
            if (current.region.x1 == other.region.x1 and current.region.x2 == other.region.x2) or \
               (current.region.y1 == other.region.y1 and current.region.y2 == other.region.y2):
                # Merge the regions
                x1 = min(current.region.x1, other.region.x1)
                y1 = min(current.region.y1, other.region.y1)
                x2 = max(current.region.x2, other.region.x2)
                y2 = max(current.region.y2, other.region.y2)
                merged_region = GridRegion([GridPoint(x1, y1), GridPoint(x2, y2)])
                merged_obj = SubGrid(merged_region, current.parent_grid)
                remaining_objects.pop(i)
                remaining_objects.insert(0, merged_obj)
                merged = True
                break
        if not merged:
            merged_objects.append(current)
    return [*new_objects, *merged_objects]

show_count = 0
def move_and_check(grid, movable_obj, fixed_obj, move_point, fixed_obj_color):
    global show_count
    new_grid = grid.copy()
    # movable_obj.region.x1, y1 is empty. so iterater and find new move_point
    # plot_grids([grid, movable_obj, fixed_obj], show=1, save_all=True)
    if move_point.x == 0:
        # check across the left column
        for row in range(movable_obj.height):
                if movable_obj[row][0] != grid.background_color:
                    new_x1 = 0
                    new_y1 = row
                    break
    if move_point.y == grid.height - 1:
        # check across the bottom row
        for col in range(movable_obj.width):
            if movable_obj[movable_obj.height-1][col] != grid.background_color:
                new_x1 = col
                new_y1 = movable_obj.height-1
                break
    if move_point.x == grid.width - 1:
        # check across the right column
        for row in range(movable_obj.height):
            if movable_obj[row][movable_obj.width-1] != grid.background_color:
                new_x1 = movable_obj.width-1
                new_y1 = row
                break
    if move_point.y == 0:
        # check across the top row
        for col in range(movable_obj.width):
            if movable_obj[0][col] != grid.background_color:
                new_x1 = col
                new_y1 = 0
                break
    
    fixed_obj_total_dots = fixed_obj.get_total_dots()
    new_grid = move_object(movable_obj, 
                          move_point.x - new_x1 - movable_obj.region.x1,
                          move_point.y - new_y1 - movable_obj.region.y1,
                          new_grid)
    show_count += 1
    # plot_grids([grid, movable_obj, new_grid], show=show_count>=1, save_all=True)
    # Check if the fit is valid (no color conflicts)
    fit_valid = True
    fixed_obj_total_dots_count = 0
    for row in range(fixed_obj.region.y1, fixed_obj.region.y2 + 1):
        for col in range(fixed_obj.region.x1, fixed_obj.region.x2 + 1):
            if new_grid[row][col] == fixed_obj_color:
                fixed_obj_total_dots_count += 1
            if new_grid[row][col] == grid.background_color:
                fit_valid = False
                break
        if not fit_valid:
            break
    if fixed_obj_total_dots_count != fixed_obj_total_dots:
        fit_valid = False
    return fit_valid, new_grid

def fit_or_swap_fit(grid):
    # two objects
    # a - one color is fixed
    # b - two colors are movable
    # fit b into a (one color should be fully fitted)
    # if swap is needed, swap the two colors too.
    
    # Detect objects in the grid
    objects = detect_objects(grid)
    objects = merge_objects(objects)
    fixed_objs = []
    movable_objs = []
    for obj in objects:
        colors = list(obj.get_values_count().keys())
        if len(colors) == 1:
            fixed_objs.append(obj)
        else:
            movable_objs.append(obj)
    
    mapper = {}
    for fixed_obj in fixed_objs:
        # find number of holes in the fixed obj
        holes = 0
        for row in range(fixed_obj.region.y1, fixed_obj.region.y2 + 1):
            for col in range(fixed_obj.region.x1, fixed_obj.region.x2 + 1):
                if grid[row][col] == grid.background_color:
                    holes += 1
        mapper[holes] = [fixed_obj]
    
    for movable_obj in movable_objs:
        total_dots_count = movable_obj.get_values_count().values()
        for count in total_dots_count:
            if count in mapper:
                mapper[count].append(movable_obj)
                break
    
    initial_grid = grid.copy()
    for idx, (hole_count, (fixed_obj, movable_obj)) in enumerate(list(mapper.items())):
        # Get the fixed color
        fixed_obj_color = list(fixed_obj.get_values_count().keys())[0]
        
        # Get the two colors from movable object
        movable_obj_colors = list(movable_obj.get_values_count().keys())
    
        # Try to fit the movable object into the fixed object
        # First try without swapping colors
        # find the first empty dot inside the fixed obj
        # plot_grid(fixed_obj, show=1, save_all=True)
        fixed_obj_attached_side = 'left' if fixed_obj.region.x1 == 0 else 'right' if fixed_obj.region.x2 == grid.width - 1 else 'bottom' if fixed_obj.region.y2 == grid.height - 1 else 'top'
        if fixed_obj_attached_side == 'left':
            col = fixed_obj.region.x1
            move_point = None
            for row in range(fixed_obj.region.y1, fixed_obj.region.y2 + 1):
                # print(row, col, grid[row][col], flush=True)
                if grid[row][col] == grid.background_color:
                    move_point = GridPoint(col, row)
                    break
        elif fixed_obj_attached_side == 'right':
            col = fixed_obj.region.x2
            move_point = None
            for row in range(fixed_obj.region.y1, fixed_obj.region.y2 + 1):
                if grid[row][col] == grid.background_color:
                    move_point = GridPoint(col, row)
                    break
        elif fixed_obj_attached_side == 'bottom':
            row = fixed_obj.region.y2
            move_point = None
            for col in range(fixed_obj.region.x1, fixed_obj.region.x2 + 1):
                if grid[row][col] == grid.background_color:
                    move_point = GridPoint(col, row)
                    break
        elif fixed_obj_attached_side == 'top':
            row = fixed_obj.region.y1
            move_point = None
            for col in range(fixed_obj.region.x1, fixed_obj.region.x2 + 1):
                if grid[row][col] == grid.background_color:
                    move_point = GridPoint(col, row)
                    break
        logger.debug(f'move_point: {move_point}')
        # rotate movable_obj 90, 180, 270 degrees
        initial_movable_obj = movable_obj.copy()
        initial_grid.remove_object(movable_obj)
        fit_valid = False
        if 1:
            for _ in range(4):
                grid = initial_grid.copy()
                fit_valid, new_grid = move_and_check(grid, movable_obj, fixed_obj, move_point, fixed_obj_color)
                if fit_valid:
                    break
                movable_obj = rotate_object(movable_obj)
        if not fit_valid:
            # Try swapping colors
            new_grid = initial_grid.copy()
            movable_obj = initial_movable_obj.copy()
            # flip the movable object and swap the colors
            for row in range(movable_obj.height):
                for col in range(movable_obj.width):
                    new_value  = initial_movable_obj[row][movable_obj.width - col - 1]
                    if new_value == movable_obj_colors[0]:
                        new_value = movable_obj_colors[1]
                    elif new_value == movable_obj_colors[1]:
                        new_value = movable_obj_colors[0]
                    movable_obj[row][col] = new_value
            initial_new_grid = new_grid.copy()
            for _ in range(4):
                new_grid = initial_new_grid.copy()
                fit_valid, new_grid = move_and_check(new_grid, movable_obj, fixed_obj, move_point, fixed_obj_color)
                if fit_valid:
                    break
                movable_obj = rotate_object(movable_obj)
            # plot_grids([grid, new_grid], show=1, save_all=True)      
        initial_grid = new_grid.copy()
        # plot_grids([grid, movable_obj, fixed_obj, new_grid], show=1, save_all=True)
    return new_grid

if __name__ == "__main__":
    import os
    os.system("main.py a25697e4 fit_or_swap_fit")
