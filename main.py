from asyncio.log import logger
from copy import deepcopy
from itertools import combinations
import os
from glob import glob
import json
from arc_tools.grid import Grid, detect_objects
from arc_tools.hollow_count import count_hollows_task
from arc_tools.check_fit import check_fit
from arc_tools.plot import plot_grid, plot_grids

files = glob('C:/Users/smart/Desktop/GD/ARC-AGI-2/data/evaluation/*.json')
file = files[14]
# print(file)
file = r'C:/Users/smart/Desktop/GD/ARC-AGI-2/data/evaluation/b5ca7ac4.json'
data = json.load(open(file, 'r'))
show_count = 0
task_count = 0
skip_train = 0

from collections import Counter, deque # Add deque import
from arc_tools.grid import SubGrid # Add SubGrid import

from typing import Tuple, Set # Add typing imports

from arc_tools.grid import Color
from arc_tools.grid import move_object
def move_object_without_collision(grid: Grid) -> Grid:
    global show_count
    objects = detect_objects(grid, required_object = 'square')
    blue_objects = [obj for obj in objects if obj.grid[0][0]==Color.LIGHTBLUE.value]
    blue_objects.sort(key=lambda x: x.region.x1)
    red_objects = [obj for obj in objects if obj.grid[0][0]==Color.RED.value]
    red_objects.sort(key=lambda x: x.region.x1, reverse=True)
    logger.info(f"Total objects: {len(objects)}, blue_objects: {len(blue_objects)}, red_objects: {len(red_objects)}")

    left_side_grid = grid.copy()
    # remove red object
    for obj in red_objects:
            left_side_grid.remove_object(obj)
    # move blue object to the left side
    # sort blue objects by x1
    
    for obj in blue_objects:
        for i in range(obj.region.x1):
            # Check if all rows in the object's height range have space
            all_rows_clear = True
            for y in range(obj.region.y1, obj.region.y2 + 1):
                if left_side_grid.grid[y][i] != left_side_grid.background_color:
                    all_rows_clear = False
                    break
            
            if all_rows_clear:
                left_side_grid.remove_object(obj)
                left_side_grid = move_object(obj, -(obj.region.x1 - i), 0, left_side_grid)
                break
    right_side_grid = grid.copy()
    # remove blue object
    for obj in blue_objects:
        right_side_grid.remove_object(obj)
    # move red object to the right side
    for obj in red_objects:
        grid_width = len(right_side_grid.grid[0])
        for i in reversed(range(obj.region.x2, grid_width)):  # Start from current position to right edge
            # Check if all rows in the object's height range have space
            all_rows_clear = True
            for y in range(obj.region.y1, obj.region.y2 + 1):
                if right_side_grid.grid[y][i] != right_side_grid.background_color:
                    all_rows_clear = False
                    break
            
            if all_rows_clear:
                right_side_grid.remove_object(obj)
                right_side_grid = move_object(obj, (i - obj.region.x2), 0, right_side_grid)
                break
    # merge left with right
    for i in range(len(left_side_grid.grid)):
        for j in range(len(left_side_grid.grid[0])):
            if left_side_grid.grid[i][j] != left_side_grid.background_color:
                right_side_grid.grid[i][j] = left_side_grid.grid[i][j]
    return right_side_grid

if __name__ == "__main__":
    tasks = [
        # count_hollows_task,
        # check_fit
        move_object_without_collision
    ]
    for task in tasks:
        print(task.__name__)
        right_task = True
        for split in ['train', 'test']:
            is_incorrect = False
            for task_id in range(len(data[split])):
                if skip_train and split == 'train':
                    continue
                task_count += 1
                if task_count <= 2 and 0:
                    continue
                initial_grid_matrix = (data[split][task_id]['input'])
                grid = Grid(initial_grid_matrix)
                # from custom_input import grid
                expected_output = Grid(data[split][task_id]['output'])
                plot_grid(expected_output, name="expected_output.png")

                # grid = [[5 if j != 0 else j for j in i[:]] for i in grid]

                plot_grid(grid, name="input.png")

                output = task(grid)
                plot_grid(output, name="actual_output.png")
                if output == expected_output:
                    print(f"Correct: {task.__name__}")
                else:
                    print("Incorrect")
                    is_incorrect = True
                    break
            if is_incorrect:
                right_task = False
                break
        if right_task:
            print(f"Found right task: {task.__name__}")
            break

