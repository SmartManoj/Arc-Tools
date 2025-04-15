from collections import Counter, deque
from arc_tools.grid import Grid, detect_objects, Color, SubGrid, GridRegion, GridPoint
from arc_tools.plot import plot_grid, plot_grids
from arc_tools.logger import logger
import logging
import traceback

def get_outermost_corners(objects: list[SubGrid], input_grid: Grid, border_color: Color):
    """
    For each detected object in the grid, find its four outermost corners,
    count how many are empty (background color), and return a sorted list
    of (object, empty_corner_count) pairs, sorted by empty_corner_count.
    Also establishes parent-child relationships between objects.
    """
    bg = input_grid.background_color
    
    # Initialize parent attribute for all objects
    for obj in objects:
        obj.parent = None # type: ignore
    
    
    parent_objects = []
    for obj in objects:
        cardinals = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        empty_count = 0
        for x, y in cardinals:
            nx, ny = obj.region.x1 + x, obj.region.y1 + y
            if 0 <= nx < input_grid.width and 0 <= ny < input_grid.height:
                if input_grid[ny][nx] == bg:
                    empty_count += 1
        if empty_count <= 2:
            parent_objects.append(obj)

    objects_positions = {}
    for obj in objects:
        objects_positions[(obj.region.x1, obj.region.y1)] = obj

    new_objects = parent_objects.copy()
    def get_children(obj: SubGrid, new_objects: list[SubGrid]):
        ordinals = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for x, y in ordinals:
            nx, ny = obj.region.x1 + x, obj.region.y1 + y
            if 0 <= nx < input_grid.width and 0 <= ny < input_grid.height:
                if input_grid[ny][nx] not in [bg, border_color]:
                    new_obj = objects_positions[(nx, ny)]
                    if new_obj not in new_objects:
                        new_objects.append(new_obj)
                        return get_children(new_obj, new_objects)
        return new_objects
    
    for obj in parent_objects:
        new_objects = get_children(obj, new_objects)
    
    # add remaining objects to new_objects
    for obj in objects:
        if obj not in new_objects:
            new_objects.append(obj)

    return new_objects

def check_dots_with_color(dots_with_color: list[tuple[GridPoint, Color]], x: int, y: int):
    return GridPoint(x, y) in (x[0] for x in dots_with_color)

def walk_around(grid: Grid, obj_color: Color, initial_x: int, initial_y: int, dots_with_color: list[tuple[GridPoint, Color]]):
    cur_x, cur_y = initial_x, initial_y
    initial_grid = grid.copy()
    cardinals = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    for k, (x, y) in enumerate(cardinals):
        if initial_grid[initial_y + y][initial_x + x] == grid.background_color:
            direction = k
            break
    started = 0
    while started < grid.width * grid.height:
        # Place color at current position
        if ((initial_grid[cur_y][cur_x] == grid.background_color or check_dots_with_color(dots_with_color, cur_x, cur_y))):
            grid[cur_y][cur_x] = obj_color
            # remove in dots_with_color
            gp = GridPoint(cur_x, cur_y)
            idx = next((i for i, x in enumerate(dots_with_color) if x[0] == gp), None)
            if idx is not None:
                logger.debug(f"Removing {gp} from dots_with_color")
                dots_with_color.remove(dots_with_color[idx])
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
                logger.debug(f"Changed direction to left at {next_x}, {next_y}")
            
        # Stop if we've returned to initial position
        if next_x == initial_x and next_y == initial_y:
            break
        started += 1
        
        # Check if next position is out of bounds or not background
        if (next_x < 0 or next_x >= grid.width or 
            next_y < 0 or next_y >= grid.height or 
            (initial_grid[next_y][next_x] != grid.background_color and not check_dots_with_color(dots_with_color, next_x, next_y))):
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
    Draw the borders based on the corner dots.
    '''
    dots_with_color: list[tuple[GridPoint, Color]] = []
    border_color = grid.get_max_value()
    objects = detect_objects(grid, ignore_color=border_color, go_diagonal=False)
    objects = get_outermost_corners(objects, grid, border_color)
    for obj in objects:
        dots_with_color.append((GridPoint(obj.region.x1, obj.region.y1), grid[obj.region.y1][obj.region.x1]))
    # check all the corners of the object; if empty, prepend the correct corner with  -1 color to the dots_with_color
    for idx, obj in enumerate(objects):
        for dir in ((1,1), (1,-1), (-1,1), (-1,-1)):
            x, y = obj.region.x1 + dir[0], obj.region.y1 + dir[1]
            if grid[y][x] == grid.background_color:
                # check up, down, left, right; if only two are empty, then it's a corner
                up, down, left, right = grid[y-1][x], grid[y+1][x], grid[y][x-1], grid[y][x+1]
                if sum([side == grid.background_color for side in [up, down, left, right]]) == 2:
                    grid[y][x] = -1
                    dots_with_color.insert(max(0, idx - 1), (GridPoint(x, y), Color(-1)))

    k = 0
    while dots_with_color:
        dot, initial_obj_color = dots_with_color.pop(0)
        k += 1
        if k > 10 and 0:
            break
        logger.debug(f"Processing dot {k} {dot}; Remaining: {len(dots_with_color)}")
        obj_color = grid[dot.y][dot.x]
        if initial_obj_color != obj_color.value:
            continue
        initial_x, initial_y = dot.x, dot.y
        if k>=3 and 0:
            plot_grid(grid, show=1, save_all=1)
        walk_around(grid, obj_color, initial_x, initial_y, dots_with_color)
        for dir in ((1,1), (1,-1), (-1,1), (-1,-1)):
            initial_x, initial_y = dot.x, dot.y
            overflow = False
            for j in range(1,10):
                initial_x, initial_y = initial_x + dir[0], initial_y + dir[1]
                if 0 <= initial_x < grid.width and 0 <= initial_y < grid.height:
                    if grid[initial_y][initial_x] in [border_color, obj_color, grid.background_color]:
                        break
                else:
                    overflow = True
                    break
            if not overflow and grid[initial_y][initial_x] == grid.background_color and initial_x != dot.x and initial_y != dot.y:
                grid[initial_y][initial_x] = obj_color
                logger.debug(f"Adding border at {initial_x}, {initial_y}, {obj_color}")
                dots_with_color.append((GridPoint(initial_x, initial_y), obj_color))    
                break
        if not dots_with_color:
            for y in range(grid.height):
                found = False
                for x in range(grid.width):
                    if grid[y][x] == grid.background_color:
                        # collect dots by going (-1, -1)
                        colors = []
                        initial_x, initial_y = x, y
                        while 1:
                            initial_x, initial_y = initial_x - 1, initial_y - 1
                            if initial_x < 0 or initial_y < 0:
                                break
                            if grid[initial_y][initial_x] == border_color:
                                break
                            colors.append(grid[initial_y][initial_x])
                        # place the colors in (1, 1)
                        k1 = 0
                        last_color = grid[y-1][x-1]
                        colors_order = colors[::-1]
                        if last_color in colors_order:
                            idx = colors_order.index(last_color)
                            colors_order = colors_order[idx+1:] + colors_order[:idx]
                        for color in colors_order:
                            grid[y+k1][x+k1] = color
                            dots_with_color.append((GridPoint(x+k1, y+k1), color))
                            k1 += 1
                        found = True
                        break
                if found:
                    break
    # remove all the -1s
    for y in range(grid.height):
        for x in range(grid.width):
            if grid[y][x] == -1:
                grid[y][x] = grid.background_color
    return grid
if __name__ == "__main__":
    import os
    os.system("main.py 13e47133 borderize")