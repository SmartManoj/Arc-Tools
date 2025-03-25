import os
from glob import glob
import json
from hollow_count import count_hollows_task
from plot import plot_grid

files = glob('C:/Users/smart/Desktop/GD/ARC-AGI-2/data/evaluation/*.json')
file = files[4]
# print(file)
file = r'C:/Users/smart/Desktop/GD/ARC-AGI-2/data/evaluation/e3721c99.json'

data = json.load(open(file, 'r'))
skip_train = 0

for split in ['train', 'test']:
    breaked = False
    for task_id in range(len(data[split])):
        if skip_train and split == 'train':
            continue
        grid = (data[split][task_id]['input'])
        expected_output = (data[split][task_id]['output'])
        # grid = [[5 if j != 0 else j for j in i[:]] for i in grid]

        plot_grid(grid, name="input.png")
        output = count_hollows_task(grid)
        plot_grid(output, name="actual_output.png")
        plot_grid(expected_output, name="expected_output.png")
        if output == expected_output:
            print("Correct")
        else:
            print("Incorrect")
            breaked = True
            break
    if breaked:
        break
