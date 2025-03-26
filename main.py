import os
from glob import glob
import json
from arc_tools.hollow_count import count_hollows_task
from arc_tools.plot import plot_grid

files = glob('C:/Users/smart/Desktop/GD/ARC-AGI-2/data/evaluation/*.json')
file = files[4]
# print(file)
file = r'C:/Users/smart/Desktop/GD/ARC-AGI-2/data/evaluation/cbebaa4b.json'

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
        # slice -6 * -9
        output = [[i for i in row[:-8]] for row in output[:-6]]
        output2 = [[0 for _ in range(22)] for _ in range(22)]
        for i in range(len(output)):
            for j in range(len(output[i])):
                output2[i][j] = output[i][j]
        print(output2)
        plot_grid(output2, name="actual_output.png")
        plot_grid(expected_output, name="expected_output.png")
        if output == expected_output:
            print("Correct")
        else:
            print("Incorrect")
            breaked = True
            break
    if breaked:
        break
