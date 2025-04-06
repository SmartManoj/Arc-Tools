from datetime import datetime
import sys
from arc_tools import grid
from arc_tools.logger import logger
from copy import deepcopy
from itertools import combinations
import os
from glob import glob
import json
from arc_tools.grid import Grid, GridPoint, GridRegion, detect_objects, move_object_without_collision
from arc_tools.hollow_count import count_hollows_task
from arc_tools.check_fit import check_fit
from arc_tools.plot import plot_grid, plot_grids, remove_pngs
from arc_tools.squash import squash_grid
from task_118 import row_col_color_data
from task_66 import rope_stretch
from task_81 import fit_or_swap_fit
from train_tasks import color_swap_and_move_to_corner, repeat_reverse_grid
from task_87 import dot_to_object
show_count = 0

from collections import Counter, deque # Add deque import
from arc_tools.grid import SubGrid # Add SubGrid import

from typing import Sequence # Add typing imports

from arc_tools.grid import Color
from arc_tools.grid import move_object
from jigsaw import jigsaw_puzzle



remove_pngs()

if 0:
    normal_task_fns = [
            count_hollows_task,
            check_fit,
            move_object_without_collision,
            repeat_reverse_grid,
        ]
else:
    normal_task_fns = [
        # row_col_color_data,
        # color_swap_and_move_to_corner,
        # dot_to_object,
        # rope_stretch,
        fit_or_swap_fit
    ]

jigsaw_task_fns = [
    # jigsaw_puzzle,
    row_col_color_data, # can occur in normal task
]



def debug_output(grid, expected_output, output):
    print('Debugging output')
    # print which cells are different
    for i in range(len(expected_output)):
        for j in range(len(expected_output[0])):
            if expected_output[i][j] != output[i][j]:
                print(f"Cell {i}, {j} is different")
    plot_grids([grid, expected_output, output], show=1)
    breakpoint()

def find_task(grids, expected_outputs, start_train_task_id=1):
    if len(grids[0][0]) == len(expected_outputs[0][0]):
        task_fns = normal_task_fns
    else:
        task_fns = jigsaw_task_fns
    for task_fn in task_fns:
        print(task_fn.__name__)
        right_task = True
        for task_id, (grid, expected_output) in enumerate(zip(grids, expected_outputs), start_train_task_id):
            grid = Grid(grid)
            expected_output = Grid(expected_output)
            plot_grid(expected_output, name="expected_output.png")
            plot_grid(grid, name="input.png")
            output = task_fn(grid)
            plot_grid(output, name="actual_output.png")
            if not output.compare(expected_output):
                # debug_output(grid, expected_output, output)
                right_task = False
                break
            print(f'task {task_id} passed')
        if right_task:
            return task_fn
        print('--------------------------------')
    return None

def solve_task(data):
    num_train_tasks = len(data['train'])
    num_test_tasks = len(data['test'])
    logger.info(f"Number of train tasks: {num_train_tasks}, Number of test tasks: {num_test_tasks}")
    start_train_task_id = 1
    start_test_task_id = 1
    actual_task_name = None
    # start_train_task_id = 3
    # start_test_task_id = 2
    # actual_task_name = fit_or_swap_fit
    grids = []
    expected_outputs = []
    actual_outputs = []
    if not actual_task_name:
        for task_idx in range(start_train_task_id - 1, num_train_tasks):
            grids.append(data['train'][task_idx]['input'])
            expected_outputs.append(data['train'][task_idx]['output'])
        task_fn = find_task(grids, expected_outputs, start_train_task_id)
        if task_fn:
            print(f"Found task: {task_fn.__name__}")
        else:
            print(f"Task not found")
    else:
        task_fn = actual_task_name
    for task_idx in range(start_test_task_id - 1, num_test_tasks):
        grid = Grid(data['test'][task_idx]['input'])
        if task_fn:
            plot_grid(grid, name="input.png", show=0)
            expected_output = Grid(data['test'][task_idx].get('output'))
            plot_grid(expected_output, name="expected_output.png")
            
            output = task_fn(grid)
            plot_grid(output, name="actual_output.png")
            if expected_output:
                if output.compare(expected_output):
                    print(f"Test task {task_idx + 1} passed")
                else:
                    raise Exception(f"Incorrect task {task_idx + 1}: {task_fn.__name__}, Expected: {expected_output}, Actual: {output}")
            output = {"attempt_1": output, "attempt_2": output}
        else:
            output = {"attempt_1": grid, "attempt_2": grid}
        actual_outputs.append(output)
    return actual_outputs

if __name__ == "__main__":
    files = glob('C:/Users/smart/Desktop/GD/ARC-AGI-2/data/evaluation/*.json')
    file = files[14]
    task_hash = 'abc82100'
    if sys.argv[1:]:
        task_hash = sys.argv[1]
    split = ['evaluation', 'training']
    for s in split:
        file = rf'C:/Users/smart/Desktop/GD/ARC-AGI-2/data/{s}/{task_hash}.json'
        if os.path.exists(file):
            break
    data = json.load(open(file, 'r'))
    from pprint import pprint
    solve_task(data)
