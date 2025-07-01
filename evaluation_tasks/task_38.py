# optimize
import os
from collections import Counter
from typing import Optional, Tuple, List
from arc_tools.grid import Color, Grid, SubGrid, detect_objects, GridRegion, GridPoint, place_object_on_new_grid
from arc_tools import logger
from arc_tools.plot import plot_grids
from arc_tools.utils import list_strip

def find_matching_point(obj1: SubGrid, obj2: SubGrid, side: str, perfect_match: bool = True) -> Optional[Tuple[int, int]]:
    """
    Optimized version that reduces code duplication and improves performance.
    Returns (offset, overlap_size) or None if no match found.
    """
    # Early exit for incompatible objects
    if obj1.background_color != obj2.background_color:
        return None
    
    if side in ['left', 'right']:
        return _find_horizontal_match(obj1, obj2, side, perfect_match)
    else:  # 'up' or 'down'
        return _find_vertical_match(obj1, obj2, side, perfect_match)

def _find_horizontal_match(obj1: SubGrid, obj2: SubGrid, side: str, perfect_match: bool) -> Optional[Tuple[int, int]]:
    """Find horizontal matching points (left/right sides)."""
    if side == 'right':
        # obj2 to the right of obj1
        obj2_left_col_orig = [obj2[r][0] for r in range(obj2.height)]
        obj2_left_col = list_strip(obj2_left_col_orig, obj2.background_color)
        if not obj2_left_col:
            return None
            
        obj2_start_pos = obj2_left_col_orig.index(obj2_left_col[0])
        
        # Iterate through obj1's columns from left to right to find a match
        for obj1_col_idx in range(obj1.width):
            obj1_col = [obj1[r][obj1_col_idx] for r in range(obj1.height)]
            stripped_obj1_col = list_strip(obj1_col, obj1.background_color)
            
            # Check if obj2's left column matches this column of obj1
            if len(obj2_left_col) <= len(obj1_col):
                # Try to find obj2's left column within obj1's column
                for y_pos in range(len(obj1_col) - len(obj2_left_col) + 1):
                    subset = obj1_col[y_pos:y_pos + len(obj2_left_col)]
                    if subset == obj2_left_col:
                        if len(set(subset)) == len(set(obj2_left_col)) == 1:
                            if (len(obj2_left_col_orig) != len(stripped_obj1_col) and 
                                len(obj2_left_col_orig) != len(obj1_col)):
                                return None
                        # Found a match! Calculate the overlap width
                        overlap_w = obj1.width - obj1_col_idx
                        # Calculate y_offset: account for obj2's starting position
                        y_offset = y_pos - obj2_start_pos
                        return y_offset, overlap_w
            
            elif len(obj1_col) < len(obj2_left_col):
                # Try to find obj1's column within obj2's left column
                for y_pos in range(len(obj2_left_col) - len(obj1_col) + 1):
                    if obj2_left_col[y_pos:y_pos + len(obj1_col)] == obj1_col:
                        # Found a match! Calculate the overlap width
                        overlap_w = obj1_col_idx + 1
                        # Calculate y_offset: account for obj2's starting position
                        y_offset = -(y_pos - obj2_start_pos)
                        return y_offset, overlap_w
                        
    elif side == 'left':
        # obj2 to the left of obj1  
        return _find_left_match(obj1, obj2, perfect_match)
    
    return None

def _find_vertical_match(obj1: SubGrid, obj2: SubGrid, side: str, perfect_match: bool) -> Optional[Tuple[int, int]]:
    """Find vertical matching points (up/down sides)."""
    if side == 'down':
        # obj2 below obj1
        obj2_top_row_orig = list(obj2[0])
        obj2_top_row = list_strip(obj2_top_row_orig, obj2.background_color)
        if not obj2_top_row:
            return None
            
        obj2_start_pos = obj2_top_row_orig.index(obj2_top_row[0])
        
        # Iterate through obj1's rows from bottom to top to find a match
        for obj1_row_idx in range(obj1.height - 1, -1, -1):
            obj1_row = list(obj1[obj1_row_idx])
            
            # Check if obj2's top row matches this row of obj1
            if len(obj2_top_row) <= len(obj1_row):
                # Try to find obj2's top row within obj1's row
                for x_pos in range(len(obj1_row) - len(obj2_top_row) + 1):
                    sliced_obj1_row = obj1_row[x_pos:x_pos + len(obj2_top_row)]
                    if sliced_obj1_row == obj2_top_row:
                        if len(set(sliced_obj1_row)) == len(set(obj2_top_row)) == 1:
                            return None
                        # Found a match! Calculate the overlap height
                        overlap_h = obj1.height - obj1_row_idx
                        # Calculate x_offset: account for obj2's starting position
                        x_offset = x_pos - obj2_start_pos
                        return x_offset, overlap_h
            
            elif len(obj1_row) < len(obj2_top_row):
                # Try to find obj1's row within obj2's top row
                for x_pos in range(len(obj2_top_row) - len(obj1_row) + 1):
                    if obj2_top_row[x_pos:x_pos + len(obj1_row)] == obj1_row:
                        # Found a match! Calculate the overlap height
                        overlap_h = obj1.height - obj1_row_idx
                        # Calculate x_offset: account for obj2's starting position
                        x_offset = -(x_pos - obj2_start_pos)
                        return x_offset, overlap_h
                        
    elif side == 'up':
        # obj2 above obj1
        return _find_up_match(obj1, obj2, perfect_match)
    
    return None

def _find_left_match(obj1: SubGrid, obj2: SubGrid, perfect_match: bool) -> Optional[Tuple[int, int]]:
    """Optimized left match finding."""
    max_overlap = min(obj1.width, obj2.width)
    for overlap_w in range(max_overlap, 0, -1):
        obj1_cols = [[obj1[r][c] for r in range(obj1.height)] for c in range(overlap_w)]
        obj2_cols = [[obj2[r][c] for r in range(obj2.height)] for c in range(obj2.width - overlap_w, obj2.width)]
        
        obj1_rows = list(zip(*obj1_cols))
        obj2_rows = list(zip(*obj2_cols))

        if perfect_match and len(set(obj1_rows)) != len(obj1_rows):
            continue
            
        if len(set(obj1_rows)) == len(set(obj2_rows)) == 1:
            continue

        # Find matching position
        if len(obj1_rows) <= len(obj2_rows):
            for i in range(len(obj2_rows) - len(obj1_rows) + 1):
                if obj2_rows[i:i + len(obj1_rows)] == obj1_rows:
                    return -i, overlap_w
        else:
            for i in range(len(obj1_rows) - len(obj2_rows) + 1):
                if obj1_rows[i:i + len(obj2_rows)] == obj2_rows:
                    return i, overlap_w
    return None

def _find_up_match(obj1: SubGrid, obj2: SubGrid, perfect_match: bool) -> Optional[Tuple[int, int]]:
    """Optimized up match finding."""
    obj2_last_row_orig = list(obj2[obj2.height - 1])
    obj2_last_row = list_strip(obj2_last_row_orig, obj2.background_color)
    if not obj2_last_row:
        return None
        
    obj2_start_pos = obj2_last_row_orig.index(obj2_last_row[0])
    
    # Iterate through obj1's rows from top to bottom to find a match
    for obj1_row_idx in range(obj1.height):
        obj1_row = list(obj1[obj1_row_idx])
        
        # Check if obj2's last row matches this row of obj1
        if len(obj2_last_row) <= len(obj1_row):
            # Try to find obj2's last row within obj1's row
            for x_pos in range(len(obj1_row) - len(obj2_last_row) + 1):
                sliced_obj1_row = obj1_row[x_pos:x_pos + len(obj2_last_row)]
                if sliced_obj1_row == obj2_last_row:
                    if len(set(sliced_obj1_row)) == len(set(obj2_last_row)) == 1:
                        return None
                    # Found a match! Calculate the overlap height
                    overlap_h = obj1_row_idx + 1
                    # Calculate x_offset: account for obj2's starting position
                    x_offset = x_pos - obj2_start_pos
                    return x_offset, overlap_h
        
        elif len(obj1_row) < len(obj2_last_row):
            # Try to find obj1's row within obj2's last row
            for x_pos in range(len(obj2_last_row) - len(obj1_row) + 1):
                if obj2_last_row[x_pos:x_pos + len(obj1_row)] == obj1_row:
                    # Found a match! Calculate the overlap height
                    overlap_h = min(obj2.height, obj1.height - obj1_row_idx)
                    # Calculate x_offset: account for obj2's starting position
                    x_offset = -(x_pos - obj2_start_pos)
                    return x_offset, overlap_h
    
    return None

def merge_subgrids(obj1: SubGrid, obj2: SubGrid, join_side: str, offset: int, overlap_size: int) -> SubGrid:
    """Optimized merging with reduced code duplication."""
    bg_color = obj1.background_color
    
    # Calculate dimensions based on join side
    if join_side in ['left', 'right']:
        return _merge_horizontal(obj1, obj2, join_side, offset, overlap_size, bg_color)
    else:  # 'up' or 'down'
        return _merge_vertical(obj1, obj2, join_side, offset, overlap_size, bg_color)

def _merge_horizontal(obj1: SubGrid, obj2: SubGrid, join_side: str, offset: int, overlap_size: int, bg_color: int) -> SubGrid:
    """Merge objects horizontally (left/right)."""
    y_offset = offset
    overlap_width = overlap_size
    
    if join_side == 'right':
        new_width = obj1.width + max(0, obj2.width - overlap_width)
        obj1_x, obj2_x = 0, obj1.width - overlap_width
    else:  # left
        new_width = obj1.width + obj2.width - overlap_width
        obj1_x, obj2_x = obj2.width - overlap_width, 0
    
    # Calculate Y positions
    y_coords = [0, y_offset]
    min_y = min(y_coords)
    y_norm = -min_y if min_y < 0 else 0
    
    obj1_y = y_norm
    obj2_y = y_offset + y_norm
    new_height = max(obj1_y + obj1.height, obj2_y + obj2.height)
    
    # Create and populate new grid
    new_grid = Grid([[bg_color] * new_width for _ in range(new_height)], background_color=bg_color)
    
    if join_side == 'right':
        place_object_on_new_grid(obj1, obj1_x, obj1_y, new_grid)
        place_object_on_new_grid(obj2, obj2_x, obj2_y, new_grid)
    else:
        place_object_on_new_grid(obj2, obj2_x, obj2_y, new_grid)
        place_object_on_new_grid(obj1, obj1_x, obj1_y, new_grid)
    
    return SubGrid(GridRegion([GridPoint(0, 0), GridPoint(new_width - 1, new_height - 1)]), new_grid)

def _merge_vertical(obj1: SubGrid, obj2: SubGrid, join_side: str, offset: int, overlap_size: int, bg_color: int) -> SubGrid:
    """Merge objects vertically (up/down)."""
    x_offset = offset
    overlap_height = overlap_size
    
    # Calculate X positions
    x_coords = [0, x_offset]
    min_x = min(x_coords)
    x_norm = -min_x if min_x < 0 else 0
    
    obj1_x = x_norm
    obj2_x = x_offset + x_norm
    new_width = max(obj1_x + obj1.width, obj2_x + obj2.width)
    
    # Calculate Y positions with proper overlap handling
    if join_side == 'down':
        obj1_y = 0
        obj2_y = max(0, obj1.height - overlap_height)
        new_height = obj1.height + max(0, obj2.height - overlap_height)
    else:  # up
        obj2_y = -min(0, obj2.height - overlap_height)
        obj1_y = max(0, obj2.height - overlap_height)
        new_height = obj1.height + max(0, obj2.height - overlap_height)
    
    # Create and populate new grid
    new_grid = Grid([[bg_color] * new_width for _ in range(new_height)], background_color=bg_color)
    
    if join_side == 'down':
        place_object_on_new_grid(obj1, obj1_x, obj1_y, new_grid)
        place_object_on_new_grid(obj2, obj2_x, obj2_y, new_grid)
    else:
        place_object_on_new_grid(obj2, obj2_x, obj2_y, new_grid)
        place_object_on_new_grid(obj1, obj1_x, obj1_y, new_grid)
    
    return SubGrid(GridRegion([GridPoint(0, 0), GridPoint(new_width - 1, new_height - 1)]), new_grid)

def overlap(grid: Grid):
    """
    Optimized version with better algorithm and reduced complexity.
    """
    objects = detect_objects(grid)
    if not objects:
        return grid
    
    # Sort by area (largest first) for better merging order
    objects.sort(key=lambda x: x.width * x.height, reverse=True)
    
    merged_object = objects.pop(0)
    merged_count = 0
    perfect_match = True
    
    # Define join sides in order of preference
    join_sides = ['right', 'left', 'down', 'up']
    
    while objects:
        found_join = False
        best_match = None
        best_match_index = -1
        
        # Try each remaining object
        for i, next_obj in enumerate(objects):
            # Try each join side
            for side in join_sides:
                os.environ['merged_object_count'] = str(merged_count)
                match_info = find_matching_point(merged_object, next_obj, side, perfect_match)
                
                if match_info:
                    offset, overlap_size = match_info
                    # Prioritize larger overlaps for better results
                    if best_match is None or overlap_size > best_match[1]:
                        best_match = (side, offset, overlap_size)
                        best_match_index = i
                    break
        
        # Apply the best match found
        if best_match:
            side, offset, overlap_size = best_match
            merged_object = merge_subgrids(merged_object, objects[best_match_index], side, offset, overlap_size)
            objects.pop(best_match_index)
            found_join = True
            merged_count += 1
        
        # If no join found, try with relaxed matching
        if not found_join:
            if perfect_match:
                perfect_match = False
                continue
            break
    
    return merged_object

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 4e34c42c overlap")
