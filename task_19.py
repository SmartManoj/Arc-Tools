import json
from arc_tools import logger
from arc_tools.grid import Color, Grid, SubGrid, copy_object, detect_objects, rotate_object, GridRegion, GridPoint, flip_horizontally, move_object, place_object, rotate_object_counter_clockwise
from arc_tools.plot import plot_grid, plot_grids
# logger.setLevel(10)


def rotate_and_stack(grid: Grid) -> Grid:
    """ 
    if blue is not at the top or bottom, rotate counter clockwise.
    stack the blue border's side objects first in the order of the red border's side.
    """
    # find which corner is black
    for k,(y,x) in enumerate([(0,0), (0, grid.width-1), (grid.height-1, 0), (grid.height-1, grid.width-1)]):
        if grid[y][x] == Color.BLACK.value:
            if k == 0:
                if grid[0][x+1] != Color.BLUE.value:
                    grid = rotate_object_counter_clockwise(grid)
            elif k == 1:
                if grid[0][x-1] != Color.BLUE.value:
                    grid = rotate_object_counter_clockwise(grid)
            elif k == 2:
                if grid[y-1][0] != Color.BLUE.value:
                    grid = rotate_object_counter_clockwise(grid)
            elif k == 3:
                if grid[y-1][x-1] != Color.BLUE.value:
                    grid =  rotate_object_counter_clockwise(grid)
            blue_at_the_top = grid[0][1] == Color.BLUE.value
            red_at_the_left = grid[1][0] == Color.RED.value
            # crop the knowledge border
            if blue_at_the_top:
                if red_at_the_left:
                    grid = grid.crop(GridRegion([GridPoint(1, 1), GridPoint(grid.width-1, grid.height-1)]))
                else:
                    grid = grid.crop(GridRegion([GridPoint(0, 1), GridPoint(grid.width-2, grid.height-1)]))
            else:
                if red_at_the_left:
                    grid = grid.crop(GridRegion([GridPoint(1, 0), GridPoint(grid.width-1, grid.height-2)]))
                else:
                    grid = grid.crop(GridRegion([GridPoint(0, 0), GridPoint(grid.width-2, grid.height-2)]))
            break
    objects = detect_objects(grid)
    first_object = objects[0]
    first_row = [obj for obj in objects if obj.region.y1 == first_object.region.y1]
    second_row = [obj for obj in objects if obj.region.y1 != first_object.region.y1]
    if not red_at_the_left:
        first_row = first_row[::-1]
        second_row = second_row[::-1]
    if not blue_at_the_top:
        first_row, second_row = second_row, first_row
    objects = first_row + second_row
    max_width = 0
    total_height = 0
    for obj in objects:
        if obj.width > max_width:
            max_width = obj.width
        total_height += obj.height

    # total_height, max_width = max_width, total_height
    new_grid = Grid([[grid.background_color for _ in range(max_width)] for _ in range(total_height)])
    current_height = 0
    for obj in objects:
        # center the object
        x, y = (max_width - obj.width) // 2, current_height
        place_object(obj, x, y, new_grid)
        current_height += obj.height
    return new_grid

if __name__ == "__main__":
    import os
    os.environ['initial_file'] = __file__.split('.')[0]
    os.system("python main.py 291dc1e1 rotate_and_stack")