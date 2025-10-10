import os
from arc_tools.grid import Grid, detect_objects, Color
from arc_tools import logger
from arc_tools.plot import plot_grids

def equity(grid: Grid):
    '''
    make all the line length same as the center line's.
    '''
    objects = detect_objects(grid)
    obj = objects[0]
    obj2 = objects[1]
    if obj.width == 1:
        orientation = 'vertical'
        aligned_at_first_end = obj.region.y1 == obj2.region.y1
        objects.sort(key=lambda x: x.region.y1)
    elif obj.height == 1:
        orientation = 'horizontal'
        aligned_at_first_end = obj.region.x1 == obj2.region.x1
        objects.sort(key=lambda x: x.region.x1)
    else:
        orientation = 'diagonal'
        aligned_at_first_end = obj.region.x1 - obj.region.y2 == obj2.region.x1 - obj2.region.y2
        objects.sort(key=lambda x: x.region.x1 - x.region.y2)
    # plot_grids(objects)
    required_length = objects[len(objects) // 2].get_total_dots()
    
    for obj in objects:
        td = obj.get_total_dots()
        diff = required_length - td
        if orientation == 'vertical':
            if aligned_at_first_end:
                if diff > 0:
                    for y in range(diff):
                        grid[obj.region.y2 + 1 + y][obj.region.x1] = obj.color
                else:
                    for y in range(-diff):
                        grid[obj.region.y2 - y][obj.region.x1] = grid.background_color
            else:
                if diff > 0:
                    for y in range(diff):
                        grid[obj.region.y1 - 1 - y][obj.region.x1] = obj.color
                else:
                    for y in range(-diff):
                        grid[obj.region.y1 + y][obj.region.x1] = grid.background_color
        elif orientation == 'horizontal':
            if aligned_at_first_end:
                if diff > 0:
                    for x in range(diff):
                        grid[obj.region.y1][obj.region.x2 + 1 + x] = obj.color
                else:
                    for x in range(-diff):
                        grid[obj.region.y1][obj.region.x2 - x] = grid.background_color
            else:
                if diff > 0:
                    for x in range(diff):
                        grid[obj.region.y1][obj.region.x2 - 1 - x] = obj.color
                else:
                    for x in range(-diff):
                        grid[obj.region.y1][obj.region.x2 + x] = grid.background_color
        elif orientation == 'diagonal':
            if aligned_at_first_end:
                if diff > 0:
                    for k in range(diff):
                        grid[obj.region.y1 - 1 - k][obj.region.x2 + 1 + k] = obj.color
                else:
                    for k in range(-diff):
                        grid[obj.region.y1 + k][obj.region.x2 - k] = grid.background_color
            else:
                if diff > 0:
                    for k in range(diff):
                        grid[obj.region.y2 + 1 + k][obj.region.x1 - 1 - k] = obj.color
                else:
                    for k in range(-diff):
                        grid[obj.region.y2 - k][obj.region.x1 + k] = grid.background_color



    return grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py e376de54 equity") 
