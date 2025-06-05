from collections import Counter, deque
from arc_tools.constants import CARDINAL_DIRECTIONS, ORDINAL_DIRECTIONS
from arc_tools.grid import Grid, detect_objects, Color, SubGrid, GridRegion, GridPoint
from arc_tools.plot import plot_grid, plot_grids
from arc_tools.logger import logger
import logging
import traceback
# logger.setLevel(10)

def repeat_largest_pattern(grid: Grid) -> Grid:
    '''
    Find the largest pattern in the frames and repeat it.
    '''
    result = grid.copy()
    
    for row_idx in range(len(result)):
        row = result[row_idx]
        new_row = fix_repeating_pattern(row)
        if new_row is not None:
            result[row_idx] = new_row
    
    return result

def fix_repeating_pattern(row):
    '''
    Find the most common repeating pattern and extend it throughout the row.
    '''
    # Skip border rows that are likely frames
    if len(set(row)) <= 2:  # Likely a border row
        return None
    
    best_result = None
    best_changes = 0
    
    # Try different pattern lengths
    for pattern_len in range(2, min(6, len(row) // 3)):
        result = try_pattern_length(row, pattern_len)
        if result is not None:
            changes = sum(1 for i, (a, b) in enumerate(zip(row, result)) if a != b)
            if changes > best_changes:
                best_changes = changes
                best_result = result
    
    return best_result

def try_pattern_length(row, pattern_len):
    '''
    Try to find and apply a repeating pattern of a specific length.
    '''
    # Find all patterns of this length and their positions
    patterns = {}
    for i in range(len(row) - pattern_len + 1):
        pattern = tuple(row[i:i + pattern_len])
        if pattern not in patterns:
            patterns[pattern] = []
        patterns[pattern].append(i)
    
    # Find the most frequent pattern
    best_pattern = None
    best_count = 0
    
    for pattern, positions in patterns.items():
        if len(positions) >= 2:  # Reduce requirement to 2 occurrences
            # Check if positions have regular spacing
            if has_regular_spacing(positions):
                # Also check if extending this pattern would make sense
                extended_positions = get_extended_positions(positions, len(row), pattern_len)
                total_potential = len(positions) + len(extended_positions)
                
                if total_potential > best_count:
                    best_count = total_potential
                    best_pattern = pattern
    
    if best_pattern is None:
        return None
    
    # Apply the pattern
    return apply_regular_pattern(row, best_pattern, patterns[best_pattern])

def get_extended_positions(positions, row_len, pattern_len):
    '''
    Get additional positions where the pattern could be extended.
    '''
    if len(positions) < 2:
        return []
    
    # Calculate spacing
    spacings = []
    for i in range(1, len(positions)):
        spacings.append(positions[i] - positions[i-1])
    
    if not spacings:
        return []
    
    spacing = max(set(spacings), key=spacings.count)
    
    extended = []
    
    # Go backward from first position
    pos = positions[0] - spacing
    while pos >= 0 and pos + pattern_len <= row_len:
        extended.append(pos)
        pos -= spacing
    
    # Go forward from last position
    pos = positions[-1] + spacing
    while pos + pattern_len <= row_len:
        extended.append(pos)
        pos += spacing
    
    return extended

def has_regular_spacing(positions):
    '''
    Check if positions have mostly regular spacing.
    '''
    if len(positions) < 2:
        return False
    
    spacings = []
    for i in range(1, len(positions)):
        spacings.append(positions[i] - positions[i-1])
    
    # Check if most spacings are the same
    if spacings:
        most_common = max(set(spacings), key=spacings.count)
        consistent = sum(1 for s in spacings if s == most_common)
        return consistent >= len(spacings) * 0.7
    
    return False

def apply_regular_pattern(row, pattern, known_positions):
    '''
    Apply a pattern at regular intervals based on known positions.
    '''
    if len(known_positions) < 2:
        return None
    
    # Calculate the most common spacing
    spacings = []
    for i in range(1, len(known_positions)):
        spacings.append(known_positions[i] - known_positions[i-1])
    
    spacing = max(set(spacings), key=spacings.count)
    pattern_len = len(pattern)
    
    result = row[:]
    changes_made = False
    
    # Start from the first known position and apply pattern at regular intervals
    start_pos = known_positions[0]
    
    # Go forward
    pos = start_pos
    while pos + pattern_len <= len(row):
        if is_safe_position(row, pos, pattern_len):
            for i in range(pattern_len):
                if result[pos + i] != pattern[i]:
                    result[pos + i] = pattern[i]
                    changes_made = True
        pos += spacing
    
    # Go backward
    pos = start_pos - spacing
    while pos >= 0 and pos + pattern_len <= len(row):
        if is_safe_position(row, pos, pattern_len):
            for i in range(pattern_len):
                if result[pos + i] != pattern[i]:
                    result[pos + i] = pattern[i]
                    changes_made = True
        pos -= spacing
    
    return result if changes_made else None

def is_safe_position(row, pos, pattern_len):
    '''
    Check if it's safe to modify this position.
    '''
    # Don't modify border positions - first 2 and last 2 positions
    if pos < 2 or pos + pattern_len > len(row) - 2:
        return False
    
    return True
if __name__ == "__main__":
    import os
    os.system("main.py 135a2760 repeat_largest_pattern")