from datetime import datetime
import sys
from arc_tools import grid
from arc_tools.logger import logger
from copy import deepcopy
from itertools import combinations
import os
import json
from arc_tools.grid import Grid, GridPoint, GridRegion, detect_objects
from arc_tools.plot import plot_grid, plot_grids

from train_tasks import *
from evaluation_tasks.tasks import *
show_count = 0

from collections import Counter, deque # Add deque import
from arc_tools.grid import SubGrid # Add SubGrid import

from typing import Sequence # Add typing imports

from arc_tools.grid import Color
from arc_tools.grid import move_object


# Exception hook

import sys
import traceback
from types import TracebackType


def handle_exception(
    type_: type[BaseException], value: BaseException, tb: TracebackType | None
) -> None:
    traceback.print_exception(type_, value, tb)
    sys.exit(1)


sys.excepthook = handle_exception


#  =============

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
        # fit_or_swap_fit
    ]

jigsaw_task_fns = [
    # jigsaw_puzzle,
    row_col_color_data, # can occur in normal task
]


DEBUG_OUTPUT = 1
def debug_output(grid, expected_output, output, window_title='result'):
    if not DEBUG_OUTPUT:
        return
    # print which cells are different
    for row in range(len(expected_output)):
        for col in range(len(expected_output[0])):
            if (e := expected_output[row][col]) != (o := output[row][col]):
                logger.info(f"Cell at {row = }, {col = } is different: {e} != {o}")
    plot_grids([grid, expected_output, output], show=1, titles=["Input", "Expected output", "Actual output"], window_title=window_title)

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
            output = task_fn(grid.copy())
            if not expected_output.compare(output):
                debug_output(grid, expected_output, output, f'train_{task_id}_result')
                if actual_task_name:
                    raise Exception(f'Train task {task_id} failed')
                right_task = False
                break
            logger.info(f'Train task {task_id} passed')
        if right_task:
            return task_fn
        logger.info('--------------------------------')
    return None

def solve_task(data):
    start_train_task_id = 1
    start_test_task_id = 1
    actual_task_name = None
    start_train_task_id = 1
    start_test_task_id = 1
    num_train_tasks = len(data['train'])
    num_test_tasks = len(data['test'])
    logger.info(f"Number of train tasks: {num_train_tasks}, Number of test tasks: {num_test_tasks}")
    grids = []
    expected_outputs = []
    actual_outputs = []
    with open('reference_output.json', 'w') as f:
        json.dump(data['train'][0]['output'], f)
    if not actual_task_name:
        for task_idx in range(start_train_task_id - 1, num_train_tasks):
            grids.append(Grid(data['train'][task_idx]['input']))
            expected_outputs.append(data['train'][task_idx]['output'])
        task_fn = find_task(grids, expected_outputs, start_train_task_id)
        if 0:
            if task_fn:
                logger.info(f"Found task: {task_fn.__name__}")
            else:
                logger.info(f"Task not found")
    else:
        task_fn = globals()[actual_task_name]
    for task_idx in range(start_test_task_id - 1, num_test_tasks):
        grid = Grid(data['test'][task_idx]['input'])
        if task_fn:
            expected_output = Grid(data['test'][task_idx].get('output'))
            output = task_fn(grid.copy())
            if expected_output:
                if expected_output.compare(output):
                    logger.info(f"Test task {task_idx + 1} passed")
                else:
                    logger.info(f"Test task {task_idx + 1} failed")
                    debug_output(grid, expected_output, output, f'test_{task_idx + 1}_result')
                    raise Exception(f"Incorrect task {task_idx + 1}: {task_fn.__name__}, Expected: {expected_output}, Actual: {output}")
            output = {"attempt_1": output, "attempt_2": output}
        else:
            output = {"attempt_1": grid, "attempt_2": grid}
        actual_outputs.append(output)
    return actual_outputs

if __name__ == "__main__":
    if sys.argv[1:]:
        task_hash = sys.argv[1]
    else:
        print('Usage: python main.py <task_hash> <task_name>')
        exit()
    actual_task_name = sys.argv[2] if sys.argv[2:] else None
    split = ['evaluation', 'training']
    for s in split:
        file = rf'../ARC-AGI-2/data/{s}/{task_hash}.json'
        if os.path.exists(file):
            break
    data = json.load(open(file, 'r'))
    solve_task(data)
