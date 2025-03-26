from asyncio.log import logger
import copy
from itertools import combinations
import os
from glob import glob
import json
from arc_tools.hollow_count import count_hollows_task
from arc_tools.check_fit import check_fit
from arc_tools.plot import plot_grid, plot_grids

files = glob('C:/Users/smart/Desktop/GD/ARC-AGI-2/data/evaluation/*.json')
file = files[14]
# print(file)
file = r'C:/Users/smart/Desktop/GD/ARC-AGI-2/data/evaluation/b5ca7ac4.json'

data = json.load(open(file, 'r'))
skip_train = 0


task_count = 0
plot_show = 0

if __name__ == "__main__":
    tasks = [
        count_hollows_task,
        check_fit
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
                if task_count < 4 and 0:
                    continue
                initial_grid = (data[split][task_id]['input'])
                grid = copy.deepcopy(initial_grid)
                # from custom_input import grid
                expected_output = (data[split][task_id]['output'])
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

