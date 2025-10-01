import os
from arc_tools.grid import Grid, detect_objects, Color, place_object_on_new_grid, GridPoint
from arc_tools import logger
from arc_tools.plot import plot_grids
from collections import defaultdict

def find_first_blue_dot(grid: Grid):
    for y in range(len(grid)):
        for x in range(len(grid[0])):
            if grid[y][x] == Color.BLUE.value:
                return GridPoint(x, y)
    return None

def be_like_others(grid: Grid):
    '''
    Swap colors between two groups of objects while preserving their structure and position.
    '''
    objects = detect_objects(grid)
    # sort by area
    objects.sort(key=lambda x: x.area)
    # classify by color
    groups = defaultdict(list)
    for obj in objects:
        groups[obj.colors].append(obj)
    # total two group only
    groups = list(groups.values())

    for idx,group in enumerate(groups):
        for obj in group:
            grid.remove_object(obj)
            new_obj = groups[1-idx][0]
            if new_obj.width != obj.width:
                factor = obj.width//new_obj.width
                new_obj = new_obj.enlarge(factor)
            new_obj_blue_dot = find_first_blue_dot(new_obj)
            obj_blue_dot = find_first_blue_dot(obj)
            x = obj_blue_dot.x - new_obj_blue_dot.x
            y = obj_blue_dot.y - new_obj_blue_dot.y
            place_object_on_new_grid(new_obj, obj.region.x1 + x, obj.region.y1 + y, grid)
    return grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py c7f57c3e be_like_others") 
