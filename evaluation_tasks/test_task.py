import os
from collections import Counter
from arc_tools.grid import Grid, detect_objects, move_object

def transform(grid: Grid) -> Grid:
    result = grid.copy()
    objects = detect_objects(grid)
    return result

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system(r"python main.py 7b5033c1 transform")
