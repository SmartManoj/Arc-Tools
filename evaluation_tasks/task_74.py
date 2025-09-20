import os
from arc_tools.grid import Color, Grid, detect_objects, GridPoint
from arc_tools.constants import CARDINAL_DIRECTIONS
from arc_tools import logger
from arc_tools.plot import plot_grids


def walk_around(grid: Grid, obj_color: int, initial_x: int, initial_y: int):
    cur_x, cur_y = initial_x, initial_y
    initial_grid = grid.copy()
    direction = 0  # Default direction
    # Find a direction where there's a background cell adjacent to the starting position
    for k, (x, y) in enumerate(CARDINAL_DIRECTIONS):
        new_x, new_y = initial_x + x, initial_y + y
        if (0 <= new_x < grid.width and 0 <= new_y < grid.height and 
            initial_grid[new_y][new_x] == grid.background_color):
            direction = k
            break
    started = 0
    while started < grid.width * grid.height:
        # Place color at current position only if it's background
        if initial_grid[cur_y][cur_x] == grid.background_color:
            grid[cur_y][cur_x] = obj_color
        # Calculate next position based on direction
        next_x, next_y = cur_x, cur_y
        if direction == 0:  # right
            next_x += 1
            # Check if up is empty when moving right
            up_x, up_y = cur_x, cur_y - 1
            if (up_y >= 0 and initial_grid[up_y][up_x] == grid.background_color):
                next_x, next_y = up_x, up_y
                direction = 3  # Change direction to up
        elif direction == 1:  # down
            next_y += 1
            # Check if right is available when moving down
            right_x, right_y = cur_x + 1, cur_y
            if (right_x < grid.width and initial_grid[right_y][right_x] == grid.background_color):
                next_x, next_y = right_x, right_y
                direction = 0  # Change direction to right
        elif direction == 2:  # left
            next_x -= 1
            # Check if down is available when moving left
            down_x, down_y = cur_x, cur_y + 1
            if (down_y < grid.height and initial_grid[down_y][down_x] == grid.background_color):
                next_x, next_y = down_x, down_y
                direction = 1  # Change direction to down
        else:  # up
            next_y -= 1
            # Check if left is available when moving up
            left_x, left_y = cur_x - 1, cur_y
            if (left_x >= 0 and initial_grid[left_y][left_x] == grid.background_color):
                next_x, next_y = left_x, left_y
                direction = 2  # Change direction to left
            
        # Stop if we've returned to initial position
        if next_x == initial_x and next_y == initial_y:
            break
        started += 1
        
        # Check if next position is out of bounds or not background
        if (next_x < 0 or next_x >= grid.width or 
            next_y < 0 or next_y >= grid.height or 
            initial_grid[next_y][next_x] != grid.background_color):
            # Turn right
            direction = (direction + 1) % 4
            # Recalculate next position after turn
            next_x, next_y = cur_x, cur_y
            if direction == 0:  # right
                next_x += 1
            elif direction == 1:  # down
                next_y += 1
            elif direction == 2:  # left
                next_x -= 1
            else:  # up
                next_y -= 1
        
        # Update current position
        cur_x, cur_y = next_x, next_y

def borderify(grid: Grid):
    '''
    Draw borders around objects using the walk_around algorithm.
    Remove objects that are not in the frame.
    '''
    grid = grid.copy()
    initial_x, initial_y = 0, grid.height - 1
    walk_around(grid, Color.ORANGE.value, initial_x, initial_y)

    objects = detect_objects(grid)
    frame = objects[0]
    for obj in objects[1:]:
        if not frame.contains(obj):
            grid.remove_object(obj)
    return grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 8f3a5a89 borderify") 
