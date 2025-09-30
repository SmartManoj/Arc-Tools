import os
from collections import Counter, defaultdict
from statistics import mean
from typing import Dict, List, Set, Tuple

from arc_tools.grid import Grid, SubGrid, copy_object, detect_objects
from arc_tools.logger import logger
from arc_tools.plot import plot_grid, plot_grids

Block = Tuple[int, int]

def complete_pattern(current_pattern, expected_pattern):
    """Find which rows match the input and return dx,dy offsets from matching row's first column to other elements."""
    input_arr = current_pattern[0]  # Extract the row from nested list

    # Find matching rows
    matching_rows = []
    for i, row in enumerate(expected_pattern):
        if row == input_arr:
            matching_rows.append(i)


    # Use first column of matching row as anchor
    row_idx = matching_rows[0]
    anchor_pos = (row_idx, input_arr.index(1))  # First column of matching row


    offsets = []
    for row in range(len(expected_pattern)):
        for col in range(len(expected_pattern[0])):
            if row != row_idx and expected_pattern[row][col] == 1:
                dx = col - anchor_pos[1]
                dy = row - anchor_pos[0]
                offsets.append((dx, dy))

    return offsets


def cult(grid: Grid) -> Grid:
    """Copy the inside of one special 3x3 block so the whole picture matches it."""
    border_color = grid[0][0]
    objects = detect_objects(grid, ignore_colors=[border_color])

    first_obj_colors = objects[0].colors

    unique_objects = [obj for obj in objects if obj.colors != first_obj_colors]
    anchor_object = unique_objects[0]
    expected_pattern = [
                [int(value not in first_obj_colors)
                for c, value in enumerate(row_vals)]
                for r, row_vals in enumerate(anchor_object)
            ]
    start_row = grid.height - 1
    start_col = grid.width - 1
   
    positions = []
    for obj in objects:
        if obj.colors == first_obj_colors:
            continue
        row = (obj.region.y1 - 1) // 4
        col = (obj.region.x1 - 1) // 4
        if row < start_row:
            start_row = row
        if col < start_col:
            start_col = col
        positions.append((row,col))
    
    
    current_pattern = [[int((row + start_row, col + start_col) in positions)
                for col in range(anchor_object.region.width)]
                for row in range(anchor_object.region.height)
            ]
            


    offsets = complete_pattern(current_pattern, expected_pattern)
    step = anchor_object.height + 1
    for offset in offsets:
        copy_object(anchor_object, offset[0] * step, offset[1] * step, grid, silent=True)
    

    return grid


if __name__ == "__main__":
    os.environ["initial_file"] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py b99e7126 cult")
