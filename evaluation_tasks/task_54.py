import os
from arc_tools.grid import Grid, detect_objects, Color
from arc_tools import logger
from arc_tools.plot import plot_grids

def map_merge(grid: Grid):
    '''
    Grid is divided into 4 boxes. 
    Box 1 (leftmost): map/template
    Box 2 (second): pattern A  
    Box 3 (third): pattern B with key elements
    Box 4 (rightmost): merge result of patterns A and B
    '''
    grid.background_color = grid[0][0]
    boxes = detect_objects(grid)
    map_box = boxes[0]
    pattern_a_box = boxes[1]    
    pattern_b_box = boxes[2]    
    merge_box = boxes[3]
    
    box_color = merge_box.color
    
    obj = detect_objects(Grid(map_box))
    obj.sort(key=lambda x: x.area)
    key_dot = obj[0]
    key_divider = obj[1]
    # remove key dot from key_divider
    key_divider[key_dot.region.y1][key_dot.region.x1] = box_color

    key_dot_point = key_dot.points[0]
    key_divider_points = key_divider.points
    
    merge_patterns(grid, key_dot_point, key_divider_points, pattern_a_box, pattern_b_box, box_color, merge_box)
    return grid

def merge_patterns(grid, key_dot_point, key_divider_points, pattern_a_box, pattern_b_box, box_color, merge_box):
    box_height = merge_box.height
    box_width = merge_box.width

    x_coords = [p.x for p in key_divider_points]
    y_coords = [p.y for p in key_divider_points]
    
    is_horizontal = False
    if key_divider_points:
        x_range = max(x_coords) - min(x_coords) if x_coords else 0
        y_range = max(y_coords) - min(y_coords) if y_coords else 0
        if x_range > y_range:
            is_horizontal = True

    p_a = pattern_a_box
    p_b = pattern_b_box
    
    should_swap = False
    if key_divider_points:
        if is_horizontal:
            divider_y = sum(p.y for p in key_divider_points) / len(key_divider_points)
            if key_dot_point.y > divider_y:
                should_swap = True
        else: # Vertical
            divider_x = sum(p.x for p in key_divider_points) / len(key_divider_points)
            if key_dot_point.x > divider_x:
                should_swap = True
            
    if should_swap:
        p_a, p_b = p_b, p_a

    if is_horizontal:
        map_diag = {p.x: p.y for p in key_divider_points}
        for col in range(box_width):
            split_row = map_diag.get(col, key_dot_point.y)
            
            for row in range(box_height):
                abs_row = merge_box.region.y1 + row
                abs_col = merge_box.region.x1 + col
                
                if row >= split_row:
                    val = p_b[row][col]
                    if val is not None and val != box_color:
                        grid[abs_row][abs_col] = val
                
                if row <= split_row:
                    val = p_a[row][col]
                    if val is not None and val != box_color:
                        grid[abs_row][abs_col] = val
    else: # Vertical
        map_diag = {p.y: p.x for p in key_divider_points}
        for row in range(box_height):
            split_col = map_diag.get(row, key_dot_point.x)

            for col in range(box_width):
                abs_row = merge_box.region.y1 + row
                abs_col = merge_box.region.x1 + col

                if col >= split_col:
                    val = p_b[row][col]
                    if val is not None and val != box_color:
                        grid[abs_row][abs_col] = val

                if col <= split_col:
                    val = p_a[row][col]
                    if val is not None and val != box_color:
                        grid[abs_row][abs_col] = val


if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 7491f3cf map_merge") 
