import os
from arc_tools.grid import Grid, detect_objects, Color
from arc_tools import logger
from arc_tools.plot import plot_grids

def fillers(grid: Grid):
    '''
    fill the colors using hint_map
    '''
    objects = detect_objects(grid)
    for idx, obj in enumerate(objects):
        if len(obj.colors) != 1:
            objects.pop(idx)
            if obj.width >= obj.height:
                if obj.region.y1 == 0:
                    hint_map = {obj[0][x]: obj[1][x] for x in range(obj.width)}
                else:
                    hint_map = {obj[1][x]: obj[0][x] for x in range(obj.width)}
            else:
                if obj.region.x1 == 0:
                    hint_map = {obj[y][0]: obj[y][1] for y in range(obj.height)}
                else:
                    hint_map = {obj[y][1]: obj[y][0] for y in range(obj.height)}
    for obj in objects:
        if rc := hint_map.get(obj.color):
            new_obj = obj.copy()
            new_obj.background_color = obj.color
            holes = detect_objects(new_obj, go_diagonal=0)
            for hole in holes:
                if not obj.region.contains(hole.region):
                    continue
                for point in hole.points:
                    grid[point.y][point.x] = rc
    return grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py dbff022c fillers") 
