import os
from collections import Counter
from arc_tools.grid import Grid, GridRegion, detect_objects, Color
from arc_tools import logger
from arc_tools.plot import plot_grids

def rotate_n_flip(grid: Grid):
    '''
    rotate the frame and flip according to the border hints.
    '''
    objects = detect_objects(grid, ignore_colors = [Color.GRAY, Color.BLACK])
    # sort by area and get the inner object (smallest one)
    objects.sort(key=lambda x: x.area)
    obj = objects[0]
    
    # Get frame colors from the grid edges - find the most common non-black color on each edge
    frame_colors = {}
    # Top edge of grid
    top_colors = [grid[0][x] for x in range(grid.width) if grid[0][x] != Color.BLACK.value]
    frame_colors['top'] = Color(Counter(top_colors).most_common(1)[0][0]) if top_colors else None
    # Bottom edge of grid
    bottom_colors = [grid[grid.height-1][x] for x in range(grid.width) if grid[grid.height-1][x] != Color.BLACK.value]
    frame_colors['bottom'] = Color(Counter(bottom_colors).most_common(1)[0][0]) if bottom_colors else None
    # Left edge of grid
    left_colors = [grid[y][0] for y in range(grid.height) if grid[y][0] != Color.BLACK.value]
    frame_colors['left'] = Color(Counter(left_colors).most_common(1)[0][0]) if left_colors else None
    # Right edge of grid
    right_colors = [grid[y][grid.width-1] for y in range(grid.height) if grid[y][grid.width-1] != Color.BLACK.value]
    frame_colors['right'] = Color(Counter(right_colors).most_common(1)[0][0]) if right_colors else None
    
    
    # Try all 8 orientations (4 rotations × 2 flips)
    best_obj = obj
    best_matches = 0
    for rot in range(4):
        for flip in [False, True]:
            test_obj = obj
            for _ in range(rot):
                test_obj = test_obj.rotate()
            if flip:
                test_obj = test_obj.flip_horizontally()
            
            # Get border colors from the object
            obj_colors = {}
            # Top edge
            obj_top_colors = [test_obj[0][x] for x in range(test_obj.width) if test_obj[0][x] != Color.BLACK.value]
            obj_colors['top'] = Color(Counter(obj_top_colors).most_common(1)[0][0]) if obj_top_colors else None
            # Bottom edge
            obj_bottom_colors = [test_obj[test_obj.height-1][x] for x in range(test_obj.width) if test_obj[test_obj.height-1][x] != Color.BLACK.value]
            obj_colors['bottom'] = Color(Counter(obj_bottom_colors).most_common(1)[0][0]) if obj_bottom_colors else None
            # Left edge
            obj_left_colors = [test_obj[y][0] for y in range(test_obj.height) if test_obj[y][0] != Color.BLACK.value]
            obj_colors['left'] = Color(Counter(obj_left_colors).most_common(1)[0][0]) if obj_left_colors else None
            # Right edge
            obj_right_colors = [test_obj[y][test_obj.width-1] for y in range(test_obj.height) if test_obj[y][test_obj.width-1] != Color.BLACK.value]
            obj_colors['right'] = Color(Counter(obj_right_colors).most_common(1)[0][0]) if obj_right_colors else None
            
            # Check if borders match
            matches = sum([
                frame_colors['top'] == obj_colors['top'] if frame_colors['top'] and obj_colors['top'] else False,
                frame_colors['bottom'] == obj_colors['bottom'] if frame_colors['bottom'] and obj_colors['bottom'] else False,
                frame_colors['left'] == obj_colors['left'] if frame_colors['left'] and obj_colors['left'] else False,
                frame_colors['right'] == obj_colors['right'] if frame_colors['right'] and obj_colors['right'] else False
            ])
            
            if matches > best_matches:
                best_matches = matches
                best_obj = test_obj
    
    
    # Detect the core color (most common color in the object, excluding borders)
    all_colors = []
    for y in range(best_obj.height):
        for x in range(best_obj.width):
            all_colors.append(best_obj[y][x])
    core_color = Counter(all_colors).most_common(1)[0][0]
    
    # Crop only the border rows/columns that contain non-core colors
    # Find the bounding box of core-colored pixels
    top_crop = 0
    bottom_crop = 0
    left_crop = 0
    right_crop = 0
    
    # Find top crop - skip rows that are mostly non-core colors
    for y in range(best_obj.height):
        row_colors = [best_obj[y][x] for x in range(best_obj.width)]
        if Counter(row_colors).most_common(1)[0][0] == core_color:
            break
        top_crop += 1
    
    # Find bottom crop
    for y in range(best_obj.height - 1, -1, -1):
        row_colors = [best_obj[y][x] for x in range(best_obj.width)]
        if Counter(row_colors).most_common(1)[0][0] == core_color:
            break
        bottom_crop += 1
    
    # Find left crop
    for x in range(best_obj.width):
        col_colors = [best_obj[y][x] for y in range(best_obj.height)]
        if Counter(col_colors).most_common(1)[0][0] == core_color:
            break
        left_crop += 1
    
    # Find right crop
    for x in range(best_obj.width - 1, -1, -1):
        col_colors = [best_obj[y][x] for y in range(best_obj.height)]
        if Counter(col_colors).most_common(1)[0][0] == core_color:
            break
        right_crop += 1
    
    
    # Crop the border
    cropped_data = []
    for y in range(top_crop, best_obj.height - bottom_crop):
        row = []
        for x in range(left_crop, best_obj.width - right_crop):
            row.append(best_obj[y][x])
        cropped_data.append(row)
    
    cropped = Grid(cropped_data, best_obj.background_color)
    return cropped

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py fc7cae8d rotate_n_flip") 
