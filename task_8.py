from collections import Counter
from arc_tools import grid
from arc_tools.grid import Grid, detect_objects, Color, SubGrid, GridRegion, GridPoint
from arc_tools.plot import plot_grid, plot_grids
from arc_tools.logger import logger
import logging

logger.setLevel(logging.DEBUG)
def walk_around(grid: Grid, obj_color: Color, initial_x: int, initial_y: int, dots_with_color: list[tuple[GridPoint, Color]]):
    cur_x, cur_y = initial_x, initial_y
    direction = 0  # 0: right, 1: down, 2: left, 3: up
    started = 0
    initial_grid = grid.copy()
    while started < 100:
        # Place color at current position
        if initial_grid[cur_y][cur_x] == grid.background_color or GridPoint(cur_x, cur_y) in (x[0] for x in dots_with_color):
            grid[cur_y][cur_x] = obj_color
        if obj_color == 8:
            logger.info(f"Started at {cur_x}, {cur_y}")
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
        elif direction == 2:  # left
            next_x -= 1
        else:  # up
            next_y -= 1
            # Check if left is available when moving up
            left_x, left_y = cur_x - 1, cur_y
            if (left_x >= 0 and initial_grid[left_y][left_x] == grid.background_color):
                next_x, next_y = left_x, left_y
                direction = 2  # Change direction to left
                logger.info(f"Changed direction to left at {next_x}, {next_y}")
            
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

def borderize(grid: Grid) -> Grid:
    '''
    Identify the borders.
    '''
    dots_with_color = []
    border_color = grid.get_max_value()
    objects = detect_objects(grid, ignore_color=border_color, go_diagonal=False)
    for obj in objects[:]:
        dots_with_color.append((GridPoint(obj.region.x1, obj.region.y1), grid[obj.region.y1][obj.region.x1]))
    for k,(dot, initial_obj_color) in enumerate(dots_with_color):
        if k > 10 and 0:
            break
        logger.info(f"Processing dot {k} {dot} of {len(dots_with_color)}")
        obj_color = grid[dot.y][dot.x]
        if initial_obj_color != obj_color:
            continue
        initial_x, initial_y = dot.x, dot.y
        walk_around(grid, obj_color, initial_x, initial_y, dots_with_color)
        for dir in ((1,1), (1,-1), (-1,1), (-1,-1)):
            initial_x, initial_y = dot.x, dot.y
            overflow = False
            for j in range(1,10):
                initial_x, initial_y = initial_x + dir[0], initial_y + dir[1]
                if 0 <= initial_x < grid.width and 0 <= initial_y < grid.height:
                    if grid[initial_y][initial_x] in [obj_color, grid.background_color]:
                        break
                else:
                    overflow = True
                    break
            if not overflow and grid[initial_y][initial_x] == grid.background_color and initial_x != dot.x and initial_y != dot.y:
                grid[initial_y][initial_x] = obj_color
                logger.info(f"Adding border at {initial_x}, {initial_y}, {obj_color}")
                dots_with_color.append((GridPoint(initial_x, initial_y), obj_color))    
                break
                
            
                
    plot_grid(grid, show=True)
            
                
    return grid
if __name__ == "__main__":
    import os
    os.system("main.py 13e47133 borderize")