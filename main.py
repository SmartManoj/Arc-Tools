from datetime import datetime
import sys
from arc_tools import grid
from arc_tools.logger import logger
from copy import deepcopy
from itertools import combinations
import os
from glob import glob
import json
from arc_tools.grid import Grid, GridPoint, GridRegion, detect_objects
from task_111 import count_hollows_task
from task_99 import check_fit
from arc_tools.plot import plot_grid, plot_grids, remove_pngs
from arc_tools.squash import squash_grid

from train_tasks import *
from evaluation_tasks import *
show_count = 0

from collections import Counter, deque # Add deque import
from arc_tools.grid import SubGrid # Add SubGrid import

from typing import Sequence # Add typing imports

from arc_tools.grid import Color
from arc_tools.grid import move_object


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
    # print which cells are different
    for i in range(len(expected_output)):
        for j in range(len(expected_output[0])):
            if expected_output[i][j] != output[i][j]:
                print(f"Cell {i}, {j} is different")
    plot_grids([grid, expected_output, output], show=1)
    # breakpoint()

def find_task(grids, expected_outputs, start_train_task_id=1):
    if len(grids[0][0]) == len(expected_outputs[0][0]):
        task_fns = normal_task_fns
    else:
        task_fns = jigsaw_task_fns
    if actual_task_name:
        task_fns = [globals()[actual_task_name]]
    for task_fn in task_fns:
        logger.info(task_fn.__name__)
        right_task = True
        for task_id, (grid, expected_output) in enumerate(zip(grids, expected_outputs), start_train_task_id):
            expected_output = Grid(expected_output)
            plot_grid(expected_output, name="expected_output.png")
            plot_grid(grid, name="input.png")
            output = task_fn(grid)
            plot_grid(output, name="actual_output.png")
            if not output.compare(expected_output):
                # debug_output(grid, expected_output, output)
                if actual_task_name:
                    logger.info(f'Train task {task_id} failed')
                right_task = False
                break
            logger.info(f'Train task {task_id} passed')
        if right_task:
            return task_fn
        logger.info('--------------------------------')
    return None

def solve_task(data):
    num_train_tasks = len(data['train'])
    num_test_tasks = len(data['test'])
    logger.info(f"Number of train tasks: {num_train_tasks}, Number of test tasks: {num_test_tasks}")
    start_train_task_id = 1
    start_test_task_id = 1
    actual_task_name = None
    # start_train_task_id = 2
    # start_test_task_id = 2
    # actual_task_name = fit_or_swap_fit
    grids = []
    expected_outputs = []
    actual_outputs = []
    if not actual_task_name:
        for task_idx in range(start_train_task_id - 1, num_train_tasks):
            grids.append(Grid(data['train'][task_idx]['input']))
            expected_outputs.append(data['train'][task_idx]['output'])
        task_fn = find_task(grids, expected_outputs, start_train_task_id)
        if task_fn:
            logger.info(f"Found task: {task_fn.__name__}")
        else:
            logger.info(f"Task not found")
    else:
        task_fn = globals()[actual_task_name]
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
                    logger.info(f"Test task {task_idx + 1} passed")
                else:
                    logger.info(f"Test task {task_idx + 1} failed")
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
    actual_task_name = sys.argv[2] if sys.argv[2:] else None
    split = ['evaluation', 'training']
    for s in split:
        file = rf'C:/Users/smart/Desktop/GD/ARC-AGI-2/data/{s}/{task_hash}.json'
        if os.path.exists(file):
            break
    data = json.load(open(file, 'r'))
    solve_task(data)
