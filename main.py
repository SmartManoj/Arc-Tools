from arc_tools import grid
from arc_tools.logger import logger
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
# file = r'C:/Users/smart/Desktop/GD/ARC-AGI-2/data/evaluation/e3721c99.json'
# file = r'C:/Users/smart/Desktop/GD/ARC-AGI-2/data/evaluation/cbebaa4b.json'
file = r'C:/Users/smart/Desktop/GD/ARC-AGI-2/data/evaluation/b5ca7ac4.json'
data = json.load(open(file, 'r'))
show_count = 0

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

task_fns = [
        count_hollows_task,
        check_fit,
        move_object_without_collision
    ]
def debug_output(grid, expected_output, output):
    print('Debugging output')
    # print which cells are different
    for i in range(len(expected_output.grid)):
        for j in range(len(expected_output.grid[0])):
            if expected_output.grid[i][j] != output.grid[i][j]:
                print(f"Cell {i}, {j} is different")
    plot_grids([grid, expected_output, output],)
    breakpoint()

def find_task(grids, expected_outputs):
    for task_fn in task_fns:
        print(task_fn.__name__)
        right_task = True
        for grid, expected_output in zip(grids, expected_outputs):
            grid = Grid(grid)
            expected_output = Grid(expected_output)
            output = task_fn(grid)
            plot_grid(expected_output, name="expected_output.png")
            plot_grid(grid, name="input.png")
            plot_grid(output, name="actual_output.png")
            if output != expected_output:
                # debug_output(grid, expected_output, output)
                right_task = False
                break
        if right_task:
            return task_fn
        print('--------------------------------')
    return None

def solve_task(data):
    num_train_tasks = len(data['train'])
    num_test_tasks = len(data['test'])
    print(f"Number of train tasks: {num_train_tasks}, Number of test tasks: {num_test_tasks}")
    actual_task_name = None
    grids = []
    expected_outputs = []
    if not actual_task_name:
        for task_id in range(num_train_tasks):
            grids.append(data['train'][task_id]['input'])
            expected_outputs.append(data['train'][task_id]['output'])
        task_fn = find_task(grids, expected_outputs)
    else:
        task_fn = actual_task_name
    if task_fn:
        print(f"Found task: {task_fn.__name__}")
        for task_id in range(num_test_tasks):
            grid = Grid(data['test'][task_id]['input'])
            output = task_fn(grid)
            plot_grid(output, name="actual_output.png")
            expected_output = Grid(data['test'][task_id].get('output'))
            if expected_output:
                plot_grid(expected_output, name="expected_output.png")
                if output == expected_output:
                    print(f"Correct: {task_fn.__name__}")
                else:
                    print(f"Incorrect: {task_fn.__name__}, Expected: {expected_output}, Actual: {output}")
    else:
        print(f"Task not found")

if __name__ == "__main__":
    from pprint import pprint
    solve_task(data)
