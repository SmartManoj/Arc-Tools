import os
from arc_tools.grid import Color, Grid, detect_objects

from arc_tools.grid import Grid, Color, detect_objects, move_object

def close_the_lock(grid: Grid):
    """
    Moves the colored vertical bars to the top of the lock.
    """
    new_grid = grid.copy()

    # 1. Find the gray container object to determine the top boundary.
    gray_objects = detect_objects(grid, required_color=Color.GRAY)
    key_container = min(gray_objects, key=lambda obj: obj.get_total_dots())

    # find length of each key bite
    heights = []
    for col in range(0, key_container.width, 2):
        col_height = 0
        for row in range(key_container.height-1):
            if key_container[row][col] == Color.GRAY.value:
                col_height += 1
        heights.append(col_height)

    lock_bites = [3, 4 , 4 , 3]
    max_lock_bite = max(lock_bites)
    bar_objects = detect_objects(grid, ignore_color=Color.GRAY)
    bar_objects.sort(key=lambda obj: obj.region.x1)
    for bar_idx, bar_object in enumerate(bar_objects):
        need_to_move = heights[bar_idx] - (max_lock_bite - lock_bites[bar_idx])
        max_move = lock_bites[bar_idx] - bar_object.height
        dy = -min(need_to_move, max_move)
        move_object(bar_object, dx=0, dy=dy, grid=new_grid, fill_color=Color.GRAY)
    move_object(key_container, dx=3 + key_container.width, dy=0, grid=new_grid)
    return new_grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 4c3d4a41 close_the_lock") 
