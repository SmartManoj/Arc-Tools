import os
from arc_tools.grid import Grid, SubGrid, detect_objects, GridRegion, GridPoint, place_object_on_new_grid
from arc_tools import logger

def relocate_objects(grid: Grid):
    '''
    Relocate objects from right side to correct size on left side, or from bottom to top
    '''
    # Detect if we have a vertical split (left/right) or horizontal split (top/bottom)
    
    result_grid_color = grid.get_max_color()
    # Check for vertical split - scan columns from left to right
    vertical_split = None
    for col in range(1, grid.width):
        col_colors = set(grid.get(col, row) for row in range(grid.height))
        if len(col_colors) == 1 and grid.get(col, 0) == result_grid_color:
            vertical_split = True
            if grid.get(0, 0) == result_grid_color:
                result_grid_x1 = 0
                result_grid_x2 = col
            else:
                result_grid_x1 = col
                result_grid_x2 = grid.width - 1
            break
    
    # Check for horizontal split - scan rows from top to bottom  
    if not vertical_split:
        for row in range(1, grid.height):
            row_colors = set(grid.get(col, row) for col in range(grid.width))
            if len(row_colors) == 1 and grid.get(0, row) == result_grid_color:
                horizontal_split = True
                if grid.get(0, 0) == result_grid_color:
                    result_grid_y1 = 0
                    result_grid_y2 = row
                else:
                    result_grid_y1 = row
                    result_grid_y2 = grid.height - 1
                break
    
    objects = detect_objects(grid)
    # Determine which type of split we have
    if vertical_split:
        # Handle vertical split (left/right regions)
        result_grid = SubGrid(GridRegion([GridPoint(result_grid_x1, 0), GridPoint(result_grid_x2, grid.height - 1)]), grid)
        
        # Get objects from right region
        right_objects = [obj for obj in objects if obj.region.x1 >= result_grid_x1]
        
        # First, place single objects by checking for 3 frame_color dots around them
        single_objects = [obj for obj in right_objects if obj.width == 1 and obj.height == 1]
        objects_to_remove = []
        
        for col in range(result_grid.width):
            for row in range(result_grid.height):
                if result_grid.get(col, row) == grid.background_color:
                    # Check for 3 frame_color dots around this position
                    frame_color_count = 0
                    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # left, right, up, down
                    
                    for dx, dy in directions:
                        new_col, new_row = col + dx, row + dy
                        if (0 <= new_col < result_grid.width and 
                            0 <= new_row < result_grid.height and
                            result_grid.get(new_col, new_row) == result_grid_color):
                            frame_color_count += 1
                    
                    if frame_color_count == 3:
                        # Find a single object to place here
                        for obj in single_objects:
                            if obj not in objects_to_remove:
                                place_object_on_new_grid(obj, col, row, result_grid)
                                objects_to_remove.append(obj)
                                break
        
        # Remove placed objects from right_objects
        for obj in objects_to_remove:
            if obj in right_objects:
                right_objects.remove(obj)
        
        # Then, scan the left region for empty spaces and place remaining objects from right region
        for row in range(result_grid.height):
            for col in range(result_grid.width):
                if result_grid.get(col, row) == grid.background_color:
                    # Find consecutive empty cells horizontally
                    width = 0
                    for c in range(col, result_grid.width):
                        if result_grid.get(c, row) == grid.background_color:
                            width += 1
                        else:
                            break
                    x1 = col
                    x2 = c - 1
                    height = 1
                    for r in range(row+1, result_grid.height):
                        col_check = []
                        for c in range(result_grid.width):
                            col_check.append(result_grid.get(c, r) == grid.background_color)
                        if sum(col_check) == width and sum(col_check[x1:x2 + 1]) == width:
                            height += 1
                        else:
                            break
                    
                    if width > 0:
                        # Find object from remaining right region objects that fits this space
                        for obj in right_objects:
                            if obj.width == width and obj.height == height:
                                place_object_on_new_grid(obj, col, row, result_grid)
                                right_objects.remove(obj)
                                break
                    break
                    
    elif horizontal_split:
        # Handle horizontal split (top/bottom regions) - result is the bottom region
        result_grid = SubGrid(GridRegion([GridPoint(0, result_grid_y1), GridPoint(grid.width - 1, result_grid_y2)]), grid)
        # Create bottom region filled with background color (use 8 for horizontal split)
        
        # Scan the bottom region for empty spaces and place objects from top region
        objects_to_remove = []
        
        # First, place single dot objects by checking for 3 frame_color dots around them
        single_dot_objects = [obj for obj in objects if obj.width == 1 and obj.height == 1]
        
        for col in range(result_grid.width):
            for row in range(result_grid.height):
                if result_grid.get(col, row) == grid.background_color:
                    # Check for 3 frame_color dots around this position
                    frame_color_count = 0
                    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # left, right, up, down
                    
                    for dx, dy in directions:
                        new_col, new_row = col + dx, row + dy
                        if (0 <= new_col < result_grid.width and 
                            0 <= new_row < result_grid.height and
                            result_grid.get(new_col, new_row) == result_grid_color):
                            frame_color_count += 1
                    
                    if frame_color_count == 3:
                        # Find a single dot object to place here
                        for obj in single_dot_objects:
                            if obj not in objects_to_remove:
                                place_object_on_new_grid(obj, col, row, result_grid)
                                objects_to_remove.append(obj)
                                break
        
        # Remove placed objects from the main objects list
        for obj in objects_to_remove:
            if obj in objects:
                objects.remove(obj)
        
        # Then, place remaining objects using the general logic
        for col in range(result_grid.width):
            for row in range(result_grid.height):
                if result_grid.get(col, row) == grid.background_color:
                    # Find consecutive empty cells vertically
                    height = 0
                    for r in range(row, result_grid.height):
                        if result_grid.get(col, r) == grid.background_color:
                            height += 1
                        else:
                            break
                    y1 = row
                    y2 = r - 1
                    # find x2 
                    width = 1
                    for c in range(col + 1, result_grid.width):
                        col_check = []
                        for y in range(result_grid.height):
                            check = result_grid.get(c, y) == grid.background_color
                            col_check.append(check)
                        if sum(col_check) == height and sum(col_check[y1:y2 + 1]) == height:
                            width += 1
                        else:
                            break
                    if width > 0:
                        # Find object from remaining objects that fits this space
                        for obj in objects:
                            if (obj.width == width and 
                                obj.height == height and 
                                # obj.region.y2 < result_grid_y2 and
                                obj not in objects_to_remove):
                                place_object_on_new_grid(obj, col, row, result_grid)
                                objects_to_remove.append(obj)
                                break
                    break
        
        # Temporarily just return the background-filled grid to test
        return result_grid
    else:
        # Fallback: no clear split detected, return original grid
        logger.info("No clear split detected, returning original grid")
        result_grid = grid
        
    return result_grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 5dbc8537 relocate_objects") 
