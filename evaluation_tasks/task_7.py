# remove unused code
from arc_tools.grid import Grid, detect_objects, Color
from arc_tools.logger import logger

def repeat_largest_pattern(grid: Grid) -> Grid:
    '''
    Find the largest pattern in the frames and repeat it.
    Support both horizontal (row) and vertical (column) patterns.
    '''
    result = grid.copy()
    border_color = Color(grid[1][1])
    boxes = detect_objects(grid,single_color_only=0,required_color=border_color)
    first_box = boxes[0]
    if first_box.width > first_box.height:
        result = fix_column_patterns(result)
    else:
        result = fix_row_patterns(result)
    return result

def fix_column_patterns(grid: Grid) -> Grid:
    '''
    Check first 2 columns and next 2, if not matched check in reverse and go up to 3 and 4.
    Only work within the boxes.
    '''
    result = grid.copy()
    border_color = Color(grid[1][1])
    boxes = detect_objects(grid,single_color_only=0,required_color=border_color)
    
    if not boxes:
        logger.debug("No boxes found")
        return result
    
    logger.debug(f"Found {len(boxes)} boxes")
    
    # Process each box separately
    for region_idx, box in enumerate(boxes):
        logger.debug(f"Processing box {region_idx + 1}: {box}")
        result = process_box(result, grid, box)
    
    return result

def process_box(result: Grid, original_grid: Grid, box) -> Grid:
    '''
    Process a single box for column patterns.
    '''
    start_row, end_row, start_col, end_col = box.region.y1 + 1, box.region.y2 - 1, box.region.x1 + 1, box.region.x2 - 1
    red_rows = end_row - start_row + 1
    red_cols = end_col - start_col + 1
    logger.debug(f"box:  size {red_rows}x{red_cols}")
    logger.debug(f"Box region: y1={box.region.y1}, y2={box.region.y2}, x1={box.region.x1}, x2={box.region.x2}")
    logger.debug(f"Content area: start_row={start_row}, end_row={end_row}, start_col={start_col}, end_col={end_col}")
    
    # Try different column pattern sizes: 2, 3, 4 as specified
    # Collect all potential patterns and choose the best one
    potential_patterns = []
    
    for pattern_size in [2, 3, 4, 5, 6]:
        if pattern_size * 2 > red_cols:
            logger.debug(f"Skipping pattern size {pattern_size} (too large for {red_cols} columns)")
            continue
        
        logger.debug(f"Trying pattern size {pattern_size} for region with {red_cols} columns")
            
        # Extract patterns from content area only (skip box borders)
        content_start_col = start_col # Skip left border
        content_end_col = end_col      # Skip right border
        content_cols = content_end_col - content_start_col + 1
        
        # Skip if pattern is too large for content area
        if pattern_size * 2 > content_cols:
            logger.debug(f"Skipping pattern size {pattern_size} (too large for {content_cols} columns)")
            continue
        
        # Try consecutive pairs: compare columns 1,2 then 2,3 then 3,4 etc.
        found_match = False
        for start_offset in range(content_cols//pattern_size - 1):
            # Extract the first pattern_size columns from current position
            first_pattern = []
            for row in range(start_row, end_row + 1):
                pattern_row = []
                for col in range(content_start_col + start_offset * pattern_size, content_start_col + start_offset * pattern_size + pattern_size):
                    if col <= content_end_col:
                        pattern_row.append(original_grid[row][col])
                    else:
                        pattern_row.append(None)
                first_pattern.append(pattern_row)
            
            # Extract the next pattern_size columns from current position
            second_pattern = []
            for row in range(start_row, end_row + 1):
                pattern_row = []
                for col in range(content_start_col + (start_offset + 1) * pattern_size, content_start_col + (start_offset + 1) * pattern_size + pattern_size):
                    if col <= content_end_col:
                        pattern_row.append(original_grid[row][col])
                    else:
                        pattern_row.append(None)
                second_pattern.append(pattern_row)
            
            logger.debug(f"Pattern size {pattern_size}, offset {start_offset}: first={first_pattern}, second={second_pattern}")
            
            # Check if they match
            if first_pattern == second_pattern:
                logger.debug(f"Found exact matching column pattern of size {pattern_size} at offset {start_offset}")
                potential_patterns.append((pattern_size, first_pattern, "exact"))
                found_match = True
                break
        
        if found_match:
            break
    
    # Choose the best pattern from all candidates
    if potential_patterns:
        # Prefer exact matches, then larger patterns, then mostly matches
        potential_patterns.sort(key=lambda x: (x[2] == "exact", x[0], x[2] == "mostly"), reverse=True)
        best_pattern_size, best_pattern, match_type = potential_patterns[0]
        logger.debug(f"Chose pattern size {best_pattern_size} ({match_type}): {best_pattern}")
        result = apply_column_pattern_to_region(result, best_pattern, best_pattern_size, box)
        return result
    
    return result

def fix_row_patterns(grid: Grid) -> Grid:
    '''
    Check first 2 rows and next 2, if not matched check in reverse and go up to 3 and 4.
    Only work within the boxes.
    '''
    if grid is None:
        return None
    result = grid.copy()
    
    # Find ALL boxes
    frame_color = grid[1][1]
    boxes = detect_objects(grid, required_color=Color(frame_color))
    if not boxes:
        logger.debug("No boxes found for row patterns")
        return result
    
    logger.debug(f"Found {len(boxes)} boxes for row pattern processing")
    
    # Process each box separately for row patterns
    for region_idx, box in enumerate(boxes):
        logger.debug(f"Processing box {region_idx + 1} for row patterns: {box}")
        result = process_box_rows(result, grid, box)
    
    return result

def process_box_rows(result: Grid, original_grid: Grid, box) -> Grid:
    '''
    Process a single box for row patterns.
    '''
    start_row, end_row, start_col, end_col = box.region.y1 + 1, box.region.y2 - 1, box.region.x1 + 1, box.region.x2 - 1
    red_rows = end_row - start_row + 1
    red_cols = end_col - start_col + 1
    logger.debug(f"box for rows: rows {start_row}-{end_row}, cols {start_col}-{end_col}, size {red_rows}x{red_cols}")
    
    # Try different row pattern sizes: 2, 3, 4 as specified
    # Collect all potential patterns and choose the best one
    potential_patterns = []
    
    for pattern_size in [2, 3, 4, 5, 6][::-1]:
        if pattern_size * 2 > red_rows:
            logger.debug(f"Skipping row pattern size {pattern_size} (too large for {red_rows} rows)")
            continue
        
        logger.debug(f"Trying row pattern size {pattern_size} for region with {red_rows} rows")
            
        # Extract patterns from content area only (skip box borders)
        content_start_row = start_row
        content_end_row = end_row
        content_rows = content_end_row - content_start_row + 1
        
        # Skip if pattern is too large for content area
        if pattern_size * 2 > content_rows:
            continue
        
        # Try consecutive pairs: compare rows 1,2 then 2,3 then 3,4 etc.
        found_match = False
        for start_offset in range(content_rows//pattern_size - 1):
            # Extract the first pattern_size rows from current position
            first_pattern = []
            first_row_starting = content_start_row + start_offset * pattern_size
            for row in range(first_row_starting, first_row_starting + pattern_size):
                pattern_row = []
                if row <= content_end_row:
                    for col in range(start_col, end_col + 1):
                        pattern_row.append(original_grid[row][col])
                else:
                    pattern_row = [None] * (end_col - start_col)
                first_pattern.append(pattern_row)
            
            # Extract the next pattern_size rows from current position
            second_pattern = []
            second_row_starting = first_row_starting + pattern_size * 2
            for row in range(second_row_starting, second_row_starting + pattern_size):
                pattern_row = []
                if row <= content_end_row:
                    for col in range(start_col, end_col + 1):
                        pattern_row.append(original_grid[row][col])
                else:
                    pattern_row = [None] * (end_col - start_col)
                second_pattern.append(pattern_row)
            
            logger.debug(f"Row pattern size {pattern_size}, {start_offset =} {first_row_starting =} {second_row_starting =}: first={first_pattern},  second={second_pattern}")
            
            # Check if they match
            if first_pattern == second_pattern:
                logger.debug(f"Found exact matching row pattern of size {pattern_size} at offset {start_offset}")
                potential_patterns.append((pattern_size, first_pattern, "exact"))
                found_match = True
                break
        
        if found_match:
            break
    
    # Choose the best pattern from all candidates
    if potential_patterns:
        # Prefer exact matches, then larger patterns, then mostly matches
        potential_patterns.sort(key=lambda x: (x[2] == "exact", x[0], x[2] == "mostly"), reverse=True)
        best_pattern_size, best_pattern, match_type = potential_patterns[0]
        logger.debug(f"Chose row pattern size {best_pattern_size} ({match_type}): {best_pattern}")
        result = apply_row_pattern_to_region(result, best_pattern, best_pattern_size, box)
        return result
    
    return result

def apply_row_pattern_to_region(grid: Grid, pattern, pattern_size, box):
    '''
    Apply the detected row pattern only within the box.
    '''
    result = grid.copy()
    start_row, end_row, start_col, end_col = box.region.y1 + 1, box.region.y2 - 1, box.region.x1 + 1, box.region.x2 - 1
    
    logger.debug(f"Applying row pattern {pattern} to region {box}")
    logger.debug(f"Pattern size: {pattern_size}, Pattern: {pattern}")
    logger.debug(f"Box content area: rows {start_row}-{end_row}, cols {start_col}-{end_col}")
    
    # Apply the pattern by repeating it throughout the content area
    for row_idx in range(start_row, end_row + 1):
        for col_idx in range(start_col, end_col + 1):
            # Don't overwrite red border cells (value 2)
            if result[row_idx][col_idx] != 2:
                relative_row = row_idx - start_row  # Calculate relative row position
                col_offset = col_idx - start_col  # Calculate relative column position
                
                # Determine which row in the pattern to use
                pattern_row_idx = relative_row % pattern_size
                
                # Get the new value from the pattern
                if (pattern_row_idx < len(pattern) and
                    col_offset < len(pattern[pattern_row_idx]) and
                    pattern[pattern_row_idx][col_offset] is not None):
                    
                    old_val = result[row_idx][col_idx]
                    new_val = pattern[pattern_row_idx][col_offset]
                    
                    # Apply the new value
                    if old_val != new_val:
                        result[row_idx][col_idx] = new_val
                        if col_idx == start_col:  # Only log first content column changes
                            logger.debug(f"Set [{row_idx}][{col_idx}] from {old_val} to {new_val} (pattern_row={pattern_row_idx}, relative_row={relative_row})")
    
    return result


def apply_column_pattern_to_region(grid: Grid, pattern, pattern_size, box):
    '''
    Apply the detected column pattern only within the box.
    '''
    result = grid.copy()
    start_row, end_row, start_col, end_col = box.region.y1 + 1, box.region.y2 - 1, box.region.x1 + 1, box.region.x2 - 1
    
    logger.debug(f"Applying pattern {pattern} to region {box}")
    
    # For alternating patterns, determine the correct starting offset
    middle_row_idx = len(pattern) // 2
    pattern_offset = 0  # Default offset
    
    # Check if this is a true alternating pattern (size 2 with different values)
    is_alternating = (pattern_size == 2 and
                     pattern[middle_row_idx][0] is not None and
                     pattern[middle_row_idx][1] is not None and
                     pattern[middle_row_idx][0] != pattern[middle_row_idx][1])
    
    if is_alternating:
        # This is an alternating pattern, determine the correct offset
        first_content_col = start_col
        middle_row = start_row + middle_row_idx
        
        # Check what value should be at the first content position
        if first_content_col < end_col and result[middle_row][first_content_col] != 2:
            expected_first_val = result[middle_row][first_content_col]
            pattern_first_val = pattern[middle_row_idx][0]
            pattern_second_val = pattern[middle_row_idx][1]
            
            logger.debug(f"Pattern offset check: expected_first={expected_first_val}, pattern_first={pattern_first_val}, pattern_second={pattern_second_val}")
            logger.debug(f"Box coordinates: start_row={start_row}, end_row={end_row}, start_col={start_col}, end_col={end_col}")
            logger.debug(f"First content position: row={middle_row}, col={first_content_col}")
            
            # Determine if we need to start with offset 1 instead of 0
            if expected_first_val == pattern_second_val:
                pattern_offset = 1
                logger.debug(f"Using pattern offset 1")
            else:
                pattern_offset = 0
                logger.debug(f"Using pattern offset 0")
    
    # Apply the pattern throughout the box, but don't overwrite red border cells
    # For alternating patterns, apply to all content columns directly
    logger.debug(f"Applying pattern to content area: rows {start_row} to {end_row}, cols {start_col} to {end_col}")
    
    # Apply pattern to all content rows
    for row_idx in range(start_row, end_row + 1):
        logger.debug(f"Processing content row {row_idx}")
        row_pattern_idx = row_idx - start_row  # Index within the pattern
        
        # Apply pattern to all content columns in this row
        for col_idx in range(start_col, end_col + 1):
            # Don't overwrite red border cells (value 2)
            if result[row_idx][col_idx] != 2:
                old_val = result[row_idx][col_idx]
                relative_col = col_idx - start_col
                
                # Check if this is an alternating pattern (size 2 with different values)
                if (is_alternating and len(pattern) > row_pattern_idx and
                    pattern[row_pattern_idx][0] is not None and
                    pattern[row_pattern_idx][1] is not None and
                    pattern[row_pattern_idx][0] != pattern[row_pattern_idx][1]):
                    # This is an alternating pattern
                    # Apply the pattern based on column position
                    if pattern_offset == 0:
                        # Start with first value
                        new_val = pattern[row_pattern_idx][0] if relative_col % 2 == 0 else pattern[row_pattern_idx][1]
                    else:
                        # Start with second value (offset by 1)
                        new_val = pattern[row_pattern_idx][1] if relative_col % 2 == 0 else pattern[row_pattern_idx][0]
                    
                    logger.debug(f"Row {row_idx}, Column {col_idx}: relative_col={relative_col}, offset={pattern_offset}, old_val={old_val}, new_val={new_val}")
                else:
                    # Non-alternating pattern - use column offset within pattern
                    if len(pattern) > row_pattern_idx and len(pattern[row_pattern_idx]) > 0:
                        pattern_col = relative_col % pattern_size
                        if pattern_col < len(pattern[row_pattern_idx]):
                            new_val = pattern[row_pattern_idx][pattern_col]
                        else:
                            new_val = None
                    else:
                        new_val = None
                
                # Only apply if the pattern value is not None and different
                if new_val is not None and old_val != new_val:
                    result[row_idx][col_idx] = new_val
                    logger.debug(f"Set [{row_idx}][{col_idx}] from {old_val} to {new_val}")
    
    return result

if __name__ == "__main__":
    import os
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 135a2760 repeat_largest_pattern")