from collections import Counter
from arc_tools import grid
from arc_tools.grid import Grid, detect_objects, Color, SubGrid, GridRegion, GridPoint
from arc_tools.plot import plot_grid, plot_grids
from itertools import combinations
from arc_tools.logger import logger
from copy import deepcopy

def project_lines_with_gaps(grid):
    '''
    The vertical line acts as the divider.
    Identify the left and right regions relative to the divider.
    Transfer the left region to the right region.
    Insert one dot for each color in the left region at intervals based on the color count.
    If the left region is empty, transfer the right region to the left region.
    '''
    # Find the vertical line divider (column with all same color)
    divider_col = None
    divider_color = None
    direction = 1
    for col in range(len(grid[0])):
        col_colors = set(grid[row][col] for row in range(len(grid)))
        empty_col = col_colors == {Color.BLACK.value}
        if len(col_colors) == 1 and not empty_col:  # All pixels in this column are same color
            divider_col = col
            divider_color = list(col_colors)[0]
            logger.debug(f"Found divider at column {divider_col} with color {divider_color}; direction: {direction}")
            break
        
        direction = -1 if empty_col else 1


    if divider_col is None:
        logger.warning("No vertical divider line found")
        return grid
    
    # Create a copy of the grid to modify
    result = grid.copy()
    
    left_region = range(divider_col)
    right_region = range(divider_col + 1, len(grid[0]))
    if direction == -1:
        left_region, right_region = right_region[::-1], left_region[::-1]
    # For each row, find lines in the left region and project them to the right
    for y in range(len(grid)):
        # Process left region
        # First pass: collect all non-black colors in order of appearance
        color_counter = Counter()
        for x in left_region:
            color = grid[y][x]
            if color != Color.BLACK.value:
                color_counter[color] += 1
        
        # Second pass: project each color with a fixed offset
        for color, count in color_counter.items():
            # Project the color in every 4th position
            for x in right_region[::count]:
                if x < len(grid[0]):
                    result[y][x] = color
    
    
    return result

if __name__ == "__main__":
    import os
    os.system("main.py 1ae2feb7 project_lines_with_gaps")