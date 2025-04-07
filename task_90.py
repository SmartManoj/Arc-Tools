from arc_tools import logger
from arc_tools.grid import Grid, Color, detect_objects, move_object

def move_object_without_collision(grid: Grid) -> Grid:
    '''
    box shape  5x5?
    1. move light blue box to left wall
    2. move red box to right wall
    '''
    global show_count
    objects = detect_objects(grid, required_object = 'square')
    blue_objects = [obj for obj in objects if obj[0][0]==Color.LIGHTBLUE.value]
    blue_objects.sort(key=lambda x: x.region.x1)
    red_objects = [obj for obj in objects if obj[0][0]==Color.RED.value]
    red_objects.sort(key=lambda x: x.region.x1, reverse=True)
    logger.info(f"Total objects: {len(objects)}, blue_objects: {len(blue_objects)}, red_objects: {len(red_objects)}")

    left_side_grid = grid.copy()
    # remove red object
    for obj in red_objects:
            left_side_grid.remove_object(obj)
    # move blue object to the left side
    # sort blue objects by x1
    
    for obj in blue_objects:
        for i in range(obj.region.x1):
            # Check if all rows in the object's height range have space
            all_rows_clear = True
            for y in range(obj.region.y1, obj.region.y2 + 1):
                if left_side_grid[y][i] != left_side_grid.background_color:
                    all_rows_clear = False
                    break
            
            if all_rows_clear:
                left_side_grid.remove_object(obj)
                left_side_grid = move_object(obj, -(obj.region.x1 - i), 0, left_side_grid)
                break
    right_side_grid = grid.copy()
    # remove blue object
    for obj in blue_objects:
        right_side_grid.remove_object(obj)
    # move red object to the right side
    for obj in red_objects:
        grid_width = len(right_side_grid[0])
        for i in reversed(range(obj.region.x2, grid_width)):  # Start from current position to right edge
            # Check if all rows in the object's height range have space
            all_rows_clear = True
            for y in range(obj.region.y1, obj.region.y2 + 1):
                if right_side_grid[y][i] != right_side_grid.background_color:
                    all_rows_clear = False
                    break
            
            if all_rows_clear:
                right_side_grid.remove_object(obj)
                right_side_grid = move_object(obj, (i - obj.region.x2), 0, right_side_grid)
                break
    # merge left with right
    for i in range(len(left_side_grid)):
        for j in range(len(left_side_grid[0])):
            if left_side_grid[i][j] != left_side_grid.background_color:
                right_side_grid[i][j] = left_side_grid[i][j]
    return right_side_grid

if __name__ == "__main__":
    import os
    os.system("main.py b5ca7ac4 move_object_without_collision")


