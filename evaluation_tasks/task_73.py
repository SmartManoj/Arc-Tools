from collections import Counter, defaultdict
import os
from arc_tools.grid import Grid, detect_objects
from arc_tools import logger
from arc_tools.plot import plot_grids

def counter(grid: Grid):
    '''
    add the function description first.
    '''
    objects = detect_objects(grid)
    frames = []
    counter = defaultdict(int)
    for obj in objects:
        if obj.shape == (11, 5):
            frames.append(obj)
        else:
            grid.remove_object(obj)
            counter[obj.color] += 1
    
    for frame in frames:
        for i in range(counter[frame.color]):
            grid[frame.region.y1+2][frame.region.x2 - (2 * (i+1))] = frame.color

    return grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 8f215267 counter") 
