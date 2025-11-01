import os
import getpass
if getpass.getuser() == 'root':
    os.chdir('/kaggle/working/ARC-Tools/workspace')
else:
    os.chdir(r'C:\Users\smart\Desktop\GD\ARC-Tools\workspace')
from collections import Counter
from arc_tools.grid import Grid, detect_objects, move_object
from arc_tools.logger import logger
from helper import solve_task

def transform(grid: Grid) -> Grid:
    result = grid.copy()
    objects = detect_objects(grid)
    logger.info(f"Number of objects: {len(objects)}")
    # implement the logic to transform the grid here
    result = grid.copy()
    # end of logic
    return result

if __name__ == "__main__":
    solve_task(transform)
