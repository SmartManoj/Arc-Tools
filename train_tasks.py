from arc_tools.grid import Color, copy_object
from arc_tools.grid import Grid, GridPoint, GridRegion, SubGrid, detect_objects, move_object
from arc_tools.plot import plot_grid

# 1 00576224 repeat_reverse_grid
# 6 017c7c7b repeat_and_swap_color
# 709 b74ca5d1 color_swap_and_move_to_corner

def repeat_and_swap_color(grid: Grid) -> Grid:
    """
    Find the repeated region and extend it by 3 rows. Replace blue with red.
    """
    # Create a copy of the grid to avoid modifying the original
    result = grid.copy()
    
    # Find the repeated region
    # height is not fixed, so we need to find the repeated region
    # take n elements and check next n elements
    # if they are the same, then we have found the repeated region
    pattern = None
    for i in range(1, len(result) + 1):
        pattern = result[:i]
        for j in range(i, len(result), len(pattern)):
            sliced = result[j:j+len(pattern)]
            if sliced != pattern[:len(sliced)]:
                break
        else:
            break
    
    if pattern is None:
        pattern = result
    # plot_grid(pattern, name="pattern.png",show=1)
    
    # Create a new grid with exactly 3 additional rows
    new_height = len(result) + 3
    new_grid = [[result.background_color for _ in range(len(result[0]))] for _ in range(new_height)]
    
    # Copy the original grid
    for i in range(len(result)):
        for j in range(len(result[0])):
            new_grid[i][j] = result[i][j]
    
    # Add the pattern for the additional rows
    for i in range(3):
        for j in range(len(pattern[0])):
            new_grid[i+len(result)][j] = pattern[(i + len(result)) % len(pattern)][j]
    
    # Swap colors 
    for i in range(len(new_grid)):
        for j in range(len(new_grid[0])):
            if new_grid[i][j] == Color.BLUE.value:
                new_grid[i][j] = Color.RED.value
    
    return Grid(new_grid)


def repeat_reverse_grid(grid: Grid) -> Grid:
    """
    Transform a grid by repeating the grid thrice horizontally and stack them vertically in (original, reversed, original) order.
    """
    result = []
    original_grids = []
    reversed_grids = []
    
    for row in grid:
        original = [x for _ in range(3) for x in row]
        original_grids.append(original)
        
        reversed_row = list(reversed(row))
        reversed_grid = [x for _ in range(3) for x in reversed_row]
        reversed_grids.append(reversed_grid)
    
    for _ in range(3):
        result.extend(original_grids)
        result.extend(reversed_grids)
    
    return Grid(result[:len(grid) * 3])


def merge_nearby_objects_as_square(objects: list[SubGrid], background_color: int) -> list[SubGrid]:
    """
    Merge nearby objects as 5x5 square by expanding each object in all directions
    and choosing the expansion that contains the most values.
    Only combine objects if they're not already part of another potential 5x5 square.
    """
    new_objects = []
    # First, keep any objects that are already 5x5
    for obj in objects:
        if obj.height == 5 and obj.width == 5:
            new_objects.append(obj)
    objects = [o for o in objects if o not in new_objects]

    if not objects:
        return new_objects
    
    # Sort remaining objects by size
    remaining_objects = sorted(objects, key=lambda x: x.width* x.height, reverse=True)
    
    while remaining_objects:
        current_obj = remaining_objects[0]
        remaining_objects.pop(0)
        
        # Find all objects that share x or y coordinates with the current object
        aligned_objects = [current_obj]
        current_x_range = set(range(current_obj.region.x1, current_obj.region.x2 + 1))
        current_y_range = set(range(current_obj.region.y1, current_obj.region.y2 + 1))
        
        i = 0
        while i < len(remaining_objects):
            other_obj = remaining_objects[i]
            other_x_range = set(range(other_obj.region.x1, other_obj.region.x2 + 1))
            other_y_range = set(range(other_obj.region.y1, other_obj.region.y2 + 1))
            
            # Check if objects share any x or y coordinates
            if current_x_range.intersection(other_x_range) or current_y_range.intersection(other_y_range):
                # Check if adding this object would keep the total size within 5x5
                min_x = min(obj.region.x1 for obj in aligned_objects + [other_obj])
                max_x = max(obj.region.x2 for obj in aligned_objects + [other_obj])
                min_y = min(obj.region.y1 for obj in aligned_objects + [other_obj])
                max_y = max(obj.region.y2 for obj in aligned_objects + [other_obj])
                
                if (max_x - min_x + 1 <= 5) and (max_y - min_y + 1 <= 5):
                    aligned_objects.append(other_obj)
                    remaining_objects.pop(i)
                    current_x_range.update(other_x_range)
                    current_y_range.update(other_y_range)
                else:
                    i += 1
            else:
                i += 1
        
        if len(aligned_objects) > 1:
            # Find the bounding box of aligned objects
            min_x = min(obj.region.x1 for obj in aligned_objects)
            max_x = max(obj.region.x2 for obj in aligned_objects)
            min_y = min(obj.region.y1 for obj in aligned_objects)
            max_y = max(obj.region.y2 for obj in aligned_objects)
            
            # Create a grid large enough to hold all objects
            grid_size = max(10, max_x + 6, max_y + 6)
            merged_grid = [[background_color] * grid_size for _ in range(grid_size)]
            
            # Place all aligned objects in the grid
            for obj in aligned_objects:
                for i in range(obj.height):
                    for j in range(obj.width):
                        if obj[i][j] != background_color:
                            grid_y = obj.region.y1 + i
                            grid_x = obj.region.x1 + j
                            if 0 <= grid_y < grid_size and 0 <= grid_x < grid_size:
                                merged_grid[grid_y][grid_x] = obj[i][j]
            
            # Create a 5x5 region centered on the objects
            center_x = (min_x + max_x) // 2
            center_y = (min_y + max_y) // 2
            region = GridRegion([
                GridPoint(center_x - 2, center_y - 2),
                GridPoint(center_x + 2, center_y + 2)
            ])
            
            # Create the new merged object
            new_obj = SubGrid(region, Grid(merged_grid))
            new_objects.append(new_obj)
        else:
            # If no objects could be merged, keep the current object as is
            new_objects.append(current_obj)
    
    return new_objects


def color_swap_and_move_to_corner(input_grid: Grid) -> Grid:
    """
    Swap colors of the objects (5x5) in the grid and move objects by their key value to the relevent corner.
    """
    grid = input_grid.copy()
    objects = detect_objects(grid)
    corner_objects = []
    non_corner_objects = []
    for obj in objects:
        if obj.is_in_corner():
            corner_objects.append(obj)
        else:
            non_corner_objects.append(obj)
    non_corner_objects = merge_nearby_objects_as_square(non_corner_objects, grid.background_color)
    # plot_grids([*corner_objects, ], show=1)
    if 1:
        for obj in corner_objects:
            value = obj.get_min_color()
            related_objects = [o for o in non_corner_objects if value in o.get_values_count()]
            new_object = related_objects[-1].copy()
            for o in related_objects:
                for row in range(o.height):
                    for col in range(o.width):
                        if o[row][col] != grid.background_color:
                            new_object[row][col] = value
            x, y = obj.get_corner_position(new_object)
            # plot_grids([obj, new_object], show=1)
            dx, dy = x - new_object.region.x1, y - new_object.region.y1
            grid=copy_object(new_object, dx, dy, grid)


    #  swap colors in non corner objects
    for obj in non_corner_objects:
        obj_colors = set(obj.get_values_count().keys())
        for row in range(obj.region.y1, obj.region.y2 + 1):
            for col in range(obj.region.x1, obj.region.x2 + 1):
                if grid[row][col] != grid.background_color:
                    grid[row][col] = next(iter(obj_colors - {grid[row][col]}))
    return grid

if __name__ == "__main__":
    import os
    # os.system("main.py b74ca5d1 color_swap_and_move_to_corner")
    os.system("main.py 017c7c7b repeat_and_swap_color")