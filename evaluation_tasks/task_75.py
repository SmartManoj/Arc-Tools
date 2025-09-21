from math import log
import os
from arc_tools import plot
from arc_tools.grid import Grid, detect_objects
from arc_tools import logger
from arc_tools.plot import plot_grids
from collections import defaultdict

def playground(grid: Grid):
    '''
    draw borders to the playground.
    use hint obj to detect the layers.
    '''
    objects = detect_objects(grid, go_diagonal=0)
    # hint_obj is multi-color object
    # sort by colors length
    objects.sort(key=lambda x: -len(x.colors))
    hint_obj, objects = objects[0], objects[1:]
    hint_map = {x:y for x, y in hint_obj}
    # group objects by colors
    objects_by_colors = defaultdict(list)
    for obj in objects:
        objects_by_colors[obj.color].append(obj)
    visited_points = []
    for obj_color, fill_color in hint_map.items():
        objs = objects_by_colors[obj_color]
        if fill_color == grid.background_color:
            fill_color = -1
        if not objs: continue
        if len(objs) == 1:
            for x1, y1 in objs[0].points:
                grid[y1][x1] = fill_color
            continue
        x1, y1, x2, y2 = objs[0].region.x1, objs[0].region.y1, objs[1].region.x2, objs[1].region.y2
        # log all
        if x1 > x2:
            x1, x2 = objs[1].region.x1, objs[0].region.x2
        # check if object is hidden
        if grid[objs[0].region.y1][objs[0].region.x2] != obj_color:
            continue
        for x in range(x1, x2+1):
            for y in range(y1, y2+1):
                if (x,y) not in visited_points:
                    visited_points.append((x, y))
                    if grid[y][x] != obj_color:
                        grid[y][x] = fill_color
    grid.replace_color(-1, grid.background_color)
    return grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 9385bd28 playground") 
