from arc_tools import grid
from arc_tools.grid import Grid, detect_objects, Color, SubGrid, GridRegion, GridPoint
from arc_tools.plot import plot_grid, plot_grids
from itertools import combinations
from arc_tools.logger import logger

def rope_stretch(grid):
    # TODO: test all paths logic
    initial_grid = grid.copy()
    objects = detect_objects(grid)
    objects = [obj for obj in objects if obj.get_total_unique_dots() >= 2]
    sub_objs_dict = {}
    for obj in objects[:]:
        sub_objs = detect_objects(obj.get_full_grid(), single_color_only=True)
        # pole, width or height is one
        pole = [sub_obj for sub_obj in sub_objs if (sub_obj.width == 1 or sub_obj.height == 1) and sub_obj.get_total_dots() > 1][0]
        rope = [sub_obj for sub_obj in sub_objs if (sub_obj.region.y1 >= pole.region.y1 and sub_obj.region.y2 <= pole.region.y2 or sub_obj.region.x1 >= pole.region.x1 and sub_obj.region.x2 <= pole.region.x2) and not sub_obj == pole][0]
        grid.remove_object(rope)
        is_vertical = pole.height > pole.width
        rope_dots = rope.get_total_dots()
        rope_color = rope.get_max_value()
        if is_vertical:
            attached_side = 'left' if rope.region.x2 < pole.region.x1 else 'right' 
            if attached_side == 'left':
                # top right
                if top := initial_grid[rope.region.y1][rope.region.x2] != grid.background_color:
                    x, y = rope.region.x2, rope.region.y1
                # bottom right
                else:
                    x, y = rope.region.x2, rope.region.y2
            else:
                # top left
                if top := initial_grid[rope.region.y1][rope.region.x1] != grid.background_color:
                    x, y = rope.region.x1, rope.region.y1
                # bottom left
                else:
                    x, y = rope.region.x1, rope.region.y2
            current_x, current_y = x, y
            
            if attached_side == 'left':
                if top:
                    # top left
                    cover_start_point = GridPoint(max(0, pole.region.x1 - rope_dots), max(0, pole.region.y1-rope_dots))
                    cover_end_point = GridPoint(pole.region.x2, max(0,pole.region.y1-1))
                else:
                    cover_start_point = GridPoint(max(0, pole.region.x1 - rope_dots), max(0, pole.region.y2+1))
                    cover_end_point = GridPoint(pole.region.x2, min(grid.height-1,pole.region.y2+rope_dots))
            else:
                if top:
                    cover_start_point = GridPoint(pole.region.x1, max(0, rope.region.y1-rope_dots))
                    cover_end_point = GridPoint(min(grid.width-1,pole.region.x2+rope_dots), max(0,pole.region.y1-1))
                else:
                    cover_start_point = GridPoint(pole.region.x1, max(0, rope.region.y2+1))
                    cover_end_point = GridPoint(min(grid.width-1,pole.region.x2+rope_dots), min(grid.height-1,rope.region.y2+rope_dots))
            cover_region = GridRegion([cover_start_point, cover_end_point])
            cover_grid = SubGrid(cover_region, initial_grid).get_full_grid()
            cover_obj = detect_objects(cover_grid)[0]
            logger.debug(cover_obj)
            # plot_grids([cover_grid, cover_obj], show=1, save_all=True)
            wrap_points = []
            if attached_side == 'left':
                if top:
                    for x in range(cover_obj.region.x1, cover_obj.region.x2 + 1):
                        if grid[cover_obj.region.y2][x] != grid.background_color:
                            bottom_most_dot = GridPoint(x, cover_obj.region.y2)
                            break
                    if cover_obj.region.x2 < pole.region.x1:
                        # add bottom dot of cover_obj bottom most dot 
                        wrap_points.append(GridPoint(bottom_most_dot.x, bottom_most_dot.y + 1))
                    
                    for y in reversed(range(cover_obj.region.y1, cover_obj.region.y2 + 1)):
                        if grid[y][cover_obj.region.x1] != grid.background_color:
                            left_most_dot = GridPoint(cover_obj.region.x1, y)
                            break
                    for x in range(cover_obj.region.x1, cover_obj.region.x2 + 1):
                        if grid[cover_obj.region.y1][x] != grid.background_color:
                            top_most_dot = GridPoint(x, cover_obj.region.y1)
                            break
                    # add left dot of cover_obj left most dot
                    wrap_points.append(GridPoint(left_most_dot.x - 1, left_most_dot.y))
                    # add left dot of cover_obj top left
                    wrap_points.append(GridPoint(top_most_dot.x - 1, top_most_dot.y))
                    # move diagonal rope dots -1 times from pole top left dot 
                    wrap_points.append(GridPoint(pole.region.x1 + (rope_dots - 1), pole.region.y1 - (rope_dots - 1)))
                else:
                    # add left dot of cover_obj bottom left
                    wrap_points.append(GridPoint(cover_obj.region.x1 - 1, cover_obj.region.y2))
                    # move diagonal rope dots -1 times of pole bottom right dot 
                    wrap_points.append(GridPoint(pole.region.x2 + (rope_dots - 1), pole.region.y2 + (rope_dots - 1)))

            else:
                if top:
                    if cover_obj.region.x1 < pole.region.x1:
                        # add top dot of cover_obj top left
                        wrap_points.append(GridPoint(cover_obj.region.x1, cover_obj.region.y1 - 1))
                    # add right dot of cover_obj top right
                    wrap_points.append(GridPoint(cover_obj.region.x2 + 1, cover_obj.region.y1))
                    # add bottom dot of cover_obj bottom right
                    wrap_points.append(GridPoint(cover_obj.region.x2 + 1, cover_obj.region.y2))
                    # move diagonal rope dots -1 times of pole bottom right dot 
                    wrap_points.append(GridPoint(pole.region.x2 - (rope_dots - 1), pole.region.y2 - (rope_dots - 1)))
                else:
                    if cover_obj.region.x1 < pole.region.x1:
                        # add top dot of cover_obj top left
                        wrap_points.append(GridPoint(cover_obj.region.x1, cover_obj.region.y1 - 1))
                    # add right dot of cover_obj top right
                    wrap_points.append(GridPoint(cover_obj.region.x2 + 1, cover_obj.region.y1))
                    # add bottom dot of cover_obj bottom right
                    wrap_points.append(GridPoint(cover_obj.region.x2 + 1, cover_obj.region.y2))
                    # move diagonal rope dots -1 times of pole bottom right dot 
                    wrap_points.append(GridPoint(pole.region.x2 - (rope_dots - 1), pole.region.y2 + (rope_dots - 1)))
            logger.debug(wrap_points)
            
            # Create a path from the starting point to the wrap points
            remaining_dots = rope_dots
            
            # First, draw a line from the starting point to the first wrap point
            if wrap_points:
                first_point = wrap_points[0]
                # Determine direction to move
                dx = 1 if first_point.x > current_x else -1 if first_point.x < current_x else 0
                dy = 1 if first_point.y > current_y else -1 if first_point.y < current_y else 0
                
                # Calculate the number of steps needed
                x_steps = abs(first_point.x - current_x)
                y_steps = abs(first_point.y - current_y)
                max_steps = max(x_steps, y_steps)
                initial_x, initial_y = current_x, current_y
                # Draw a diagonal line (shortest path)
                for step in range(max_steps + 1):
                    if remaining_dots <= 0:
                        break
                        
                    # Calculate the current position based on step
                    logger.debug(f'Checking {current_x = }, {current_y = } {dx = } {dy = } {step = }')
                    if step <= x_steps:
                        current_x = initial_x + (dx * step)
                    if step <= y_steps:
                        current_y = initial_y + (dy * step)
                    logger.debug(f'Checking {current_x}, {current_y}')
                    # Only set the color if we're within bounds and there's no object at this position
                    if (0 <= current_y < grid.height and 0 <= current_x < grid.width and 
                        grid[current_y][current_x] == grid.background_color):
                        grid[current_y][current_x] = rope_color
                        logger.debug(f'Setting rope color at ({current_y}, {current_x})')
                        remaining_dots -= 1
                
                # Draw the remaining wrap points
                for i in range(1, len(wrap_points)):
                    if remaining_dots <= 0:
                        break
                        
                    current_point = wrap_points[i]
                    prev_point = wrap_points[i-1]
                    logger.debug(f'Drawing line from ({prev_point.y}, {prev_point.x}) to ({current_point.y}, {current_point.x})')
                    # Determine direction to move
                    dx = 1 if current_point.x > prev_point.x else -1 if current_point.x < prev_point.x else 0
                    dy = 1 if current_point.y > prev_point.y else -1 if current_point.y < prev_point.y else 0
                    
                    # Draw the line to the next wrap point
                    # Create a copy of prev_point to avoid modifying the original
                    path_point = GridPoint(prev_point.x, prev_point.y)
                    
                    # Calculate the number of steps needed
                    x_steps = abs(current_point.x - prev_point.x)
                    y_steps = abs(current_point.y - prev_point.y)
                    max_steps = max(x_steps, y_steps)
                    
                    # Draw a diagonal line (shortest path)
                    for step in range(max_steps + 1):
                        if remaining_dots <= 0:
                            break
                            
                        # Calculate the current position based on step
                        if step <= x_steps:
                            path_point.x = prev_point.x + (dx * step)
                        if step <= y_steps:
                            path_point.y = prev_point.y + (dy * step)
                            
                        # Only set the color if we're within bounds and there's no object at this position
                        if (0 <= path_point.y < grid.height and 0 <= path_point.x < grid.width and 
                            grid[path_point.y][path_point.x] == grid.background_color):
                            grid[path_point.y][path_point.x] = rope_color
                            logger.debug(f'Setting rope color at ({path_point.y}, {path_point.x})')
                            remaining_dots -= 1
        else:
            # horizontal pole
            attached_side = 'top' if rope.region.y2 < pole.region.y1 else 'bottom'
            if attached_side == 'top':
                # bottom left
                if left := initial_grid[rope.region.y2][rope.region.x1] != grid.background_color:
                    x, y = rope.region.x1, rope.region.y2
                # bottom right
                else:
                    x, y = rope.region.x2, rope.region.y2
            else:
                # top left
                if left := initial_grid[rope.region.y1][rope.region.x1] != grid.background_color:
                    x, y = rope.region.x1, rope.region.y1
                # top right
                else:
                    x, y = rope.region.x2, rope.region.y1
            current_x, current_y = x, y
            
            if attached_side == 'top':
                if left:
                    # top left
                    cover_start_point = GridPoint(max(0, pole.region.x1 - rope_dots), max(0, pole.region.y1-rope_dots))
                    cover_end_point = GridPoint(pole.region.x2, max(0,pole.region.y1-1))
                else:
                    cover_start_point = GridPoint(max(0, pole.region.x2 +  1 ), max(0, pole.region.y1-rope_dots))
                    cover_end_point = GridPoint(pole.region.x2 + rope_dots, min(grid.height-1,pole.region.y1-1))
            else:
                if left:
                    cover_start_point = GridPoint(pole.region.x1-rope_dots, max(0, rope.region.y1-rope_dots))
                    cover_end_point = GridPoint(min(grid.width-1,pole.region.x1 - 1), max(0,pole.region.y1+rope_dots))
                else:
                    cover_start_point = GridPoint(pole.region.x1, max(0, rope.region.y2+1))
                    cover_end_point = GridPoint(min(grid.width-1,pole.region.x2+rope_dots), min(grid.height-1,rope.region.y2+rope_dots))
            cover_region = GridRegion([cover_start_point, cover_end_point])
            logger.debug(cover_region)
            cover_grid = SubGrid(cover_region, initial_grid).get_full_grid()
            cover_obj = detect_objects(cover_grid)[0]
            logger.debug(cover_obj)
            wrap_points = []
            if attached_side == 'top':
                for y in range(cover_obj.region.y1, cover_obj.region.y2 + 1):
                    if grid[y][cover_obj.region.x1] != grid.background_color:
                        left_most_dot = GridPoint(cover_obj.region.x1, y)
                        break
                for x in reversed(range(cover_obj.region.x1, cover_obj.region.x2 + 1)):
                    if grid[cover_obj.region.y1][x] != grid.background_color:
                        top_right_most_dot = GridPoint(x, cover_obj.region.y1)
                        break
                # right most reversed dot
                for y in reversed(range(cover_obj.region.y1, cover_obj.region.y2 + 1)):
                    if grid[y][cover_obj.region.x2] != grid.background_color:
                        right_most_dot = GridPoint(cover_obj.region.x2, y)
                        break
                # add left dot of cover_obj left most dot
                wrap_points.append(GridPoint(left_most_dot.x - 1, left_most_dot.y))
                # add top dot of cover_obj top right most dot
                wrap_points.append(GridPoint(top_right_most_dot.x, top_right_most_dot.y - 1))
                # add right dot of cover_obj right most dot
                wrap_points.append(GridPoint(right_most_dot.x + 1, right_most_dot.y))
                # move diagonal rope dots -1 times from pole top left dot 
                wrap_points.append(GridPoint(pole.region.x1 + (rope_dots - 1), pole.region.y1 + (rope_dots - 1)))

            else:
                # add right dot of cover_obj bottom right
                wrap_points.append(GridPoint(cover_obj.region.x2 + 1, cover_obj.region.y2))
                # add bottom dot of cover_obj bottom right
                wrap_points.append(GridPoint(cover_obj.region.x2, cover_obj.region.y2 + 1))
                for x in range(cover_obj.region.x1, cover_obj.region.x2 + 1):
                    if grid[cover_obj.region.y2][x] != grid.background_color:
                        bottom_left_most_dot = GridPoint(x, cover_obj.region.y2)
                        break
                # add bottom dot of cover_obj bottom left most dot
                wrap_points.append(GridPoint(bottom_left_most_dot.x, bottom_left_most_dot.y + 1))
                # add left dot of cover_obj top left
                wrap_points.append(GridPoint(cover_obj.region.x1 - 1, cover_obj.region.y1))
                # move diagonal rope dots -1 times of pole bottom right dot 
                wrap_points.append(GridPoint(pole.region.x2 - (rope_dots - 1), pole.region.y2 - (rope_dots - 1)))
            logger.debug(wrap_points)
            
            # Create a path from the starting point to the wrap points
            remaining_dots = rope_dots
            
            # First, draw a line from the starting point to the first wrap point
            if wrap_points:
                first_point = wrap_points[0]
                # Determine direction to move
                dx = 1 if first_point.x > current_x else -1 if first_point.x < current_x else 0
                dy = 1 if first_point.y > current_y else -1 if first_point.y < current_y else 0
                
                # Calculate the number of steps needed
                x_steps = abs(first_point.x - current_x)
                y_steps = abs(first_point.y - current_y)
                max_steps = max(x_steps, y_steps)
                initial_x, initial_y = current_x, current_y
                # Draw a diagonal line (shortest path)
                for step in range(max_steps + 1):
                    if remaining_dots <= 0:
                        break
                        
                    # Calculate the current position based on step
                    logger.debug(f'Checking {current_x = }, {current_y = } {dx = } {dy = } {step = }')
                    if step <= x_steps:
                        current_x = initial_x + (dx * step)
                    if step <= y_steps:
                        current_y = initial_y + (dy * step)
                    logger.debug(f'Checking {current_x}, {current_y}')
                    # Only set the color if we're within bounds and there's no object at this position
                    if (0 <= current_y < grid.height and 0 <= current_x < grid.width and 
                        grid[current_y][current_x] == grid.background_color):
                        grid[current_y][current_x] = rope_color
                        logger.debug(f'Setting rope color at ({current_y}, {current_x})')
                        remaining_dots -= 1
                
                # Draw the remaining wrap points
                for i in range(1, len(wrap_points)):
                    if remaining_dots <= 0:
                        break
                        
                    current_point = wrap_points[i]
                    prev_point = wrap_points[i-1]
                    logger.debug(f'Drawing line from ({prev_point.y}, {prev_point.x}) to ({current_point.y}, {current_point.x})')
                    # Determine direction to move
                    dx = 1 if current_point.x > prev_point.x else -1 if current_point.x < prev_point.x else 0
                    dy = 1 if current_point.y > prev_point.y else -1 if current_point.y < prev_point.y else 0
                    
                    # Draw the line to the next wrap point
                    # Create a copy of prev_point to avoid modifying the original
                    path_point = GridPoint(prev_point.x, prev_point.y)
                    
                    # Calculate the number of steps needed
                    x_steps = abs(current_point.x - prev_point.x)
                    y_steps = abs(current_point.y - prev_point.y)
                    max_steps = max(x_steps, y_steps)
                    
                    # Draw a diagonal line (shortest path)
                    for step in range(max_steps + 1):
                        if remaining_dots <= 0:
                            break
                            
                        # Calculate the current position based on step
                        if step <= x_steps:
                            path_point.x = prev_point.x + (dx * step)
                        if step <= y_steps:
                            path_point.y = prev_point.y + (dy * step)
                            
                        # Only set the color if we're within bounds and there's no object at this position
                        if (0 <= path_point.y < grid.height and 0 <= path_point.x < grid.width and 
                            grid[path_point.y][path_point.x] == grid.background_color):
                            grid[path_point.y][path_point.x] = rope_color
                            logger.debug(f'Setting rope color at ({path_point.y}, {path_point.x})')
                            remaining_dots -= 1
                    
                    # Mark the current point
                    if (remaining_dots > 0 and 0 <= current_point.y < grid.height and 0 <= current_point.x < grid.width and
                        grid[current_point.y][current_point.x] == grid.background_color):
                        grid[current_point.y][current_point.x] = rope_color
                        logger.debug(f'Setting rope color at wrap point ({current_point.y}, {current_point.x})')
                        remaining_dots -= 1
    # plot_grids([grid], show=1, save_all=True)
    return grid

if __name__ == "__main__":
    import os
    os.system("main.py 88bcf3b4")
