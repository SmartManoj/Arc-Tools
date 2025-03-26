import json

with open('custom_input.json', 'r') as f:
    grid = json.load(f)
    for i in range(3,7):
        grid[i]= [0] + grid[i][:-1]



