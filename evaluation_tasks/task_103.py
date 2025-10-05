import os
from arc_tools.grid import Grid, detect_objects, Color
from arc_tools import logger
from arc_tools.plot import plot_grids

def spiral(grid: Grid):
    '''
    do spiral pattern from the border points
    '''
    obj = detect_objects(grid)[0]
    obj_color = obj.color
    bp = obj.get_border_points()
    
    for p in bp[:4]:
        x, y = p.x, p.y
        if p.x == obj.region.x1:
            if obj.width == 3:
                x -= 1
            direction = 0
        elif p.y == obj.region.y1:
            if obj.height == 3:
                y -= 1
            direction = 1
        elif p.x == obj.region.x2:
            if obj.width == 3:
                x += 1
            direction = 2
        else:
            if obj.height == 3:
                y += 1
            direction = 3
        half_width = obj.width//2
        segment_length = max(3, half_width + 1)
        bend_version = segment_length  != 3
        for iteration in range(1, 8):
            segment_length += (iteration + 1)
            if iteration > 3:
                segment_length -= (iteration - 3)
            if direction == 0:
                # up
                length = 0
                for k in range(segment_length):
                    length += 1
                    if y-k == -1:
                        break
                    if x>=0:
                        grid[y-k][x] = obj_color
                    if bend_version and length == max(iteration * 4 - 2, 3):
                        for l in range(half_width-1):
                            if x+l>=0:
                                grid[y-k][x+l] = obj_color
                        x += l
                        
                x += 1
                y -= segment_length - 1
            elif direction == 1:
                # right
                length = 0
                for k in range(segment_length):
                    length += 1
                    if x+k == grid.width:
                        break
                    grid[y][x+k] = obj_color
                    if bend_version and length == max(iteration * 4 - 2, 3):
                        for l in range(half_width-1):
                            grid[y+l][x+k] = obj_color
                        y += l
                y += 1
                x += segment_length - 1
            elif direction == 2:
                # down
                length = 0
                for k in range(segment_length):
                    length += 1
                    if y+k == grid.height:
                        break
                    grid[y+k][x] = obj_color
                    if bend_version and length == max(iteration * 4 - 2, 3):
                        for l in range(half_width-1):
                            grid[y+k][x-l] = obj_color
                        x -= l
                y += segment_length - 1
                x -= 1
            elif direction == 3:
                # left
                length = 0
                for k in range(segment_length):
                    length += 1
                    if x-k == -1:
                        break
                    grid[y][x-k] = obj_color
                    if bend_version and length == max(iteration * 4 - 2, 3):
                        for l in range(half_width-1):
                            grid[y-l][x-k] = obj_color
                        y -= l
                y -= 1
                x -= segment_length - 1
            direction = (direction + 1) % 4
    return grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py da515329 spiral") 
