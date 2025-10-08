import os
from arc_tools.grid import Grid, detect_objects, Color
from arc_tools import logger
from arc_tools.plot import plot_grids
from itertools import combinations

def blue_link(grid: Grid):
    '''
    Join blue dots with diagonal lines (slope +1) extending to grid boundary.
    If magenta dots exist, draw systematic diagonal lines for them.
    '''
    result = grid.copy()
    
    dots = detect_objects(grid, single_color_only=1)
    blue_dots = []
    magenta_dots = []
    for dot in dots:
        if dot.color == Color.BLUE.value:
            blue_dots.append(dot)
        elif dot.color == Color.MAGENTA.value:
            magenta_dots.append(dot)
    
    for dot_a, dot_b in combinations(blue_dots, 2):
        start_pos = dot_a.region.start
        end_pos = dot_b.region.end
        x_diff = abs(end_pos.x - start_pos.x)
        y_diff = abs(end_pos.y - start_pos.y)
        if x_diff != y_diff:
            continue
        
        if end_pos.x > start_pos.x:
            for l in range(end_pos.x - start_pos.x):
                x = start_pos.x + l
                y = start_pos.y + l
                if result.get(x, y) == Color.MAGENTA.value:
                    mx, my = (x+y, 0)
                    for m in range(x+y + 1):
                        result.set(mx, my, Color.MAGENTA.value)
                        mx -= 1
                        my += 1
                else:
                    result.set(x, y, Color.BLUE.value)
        else:
            for l in range(start_pos.x - end_pos.x):
                x = start_pos.x - l
                y = start_pos.y + l
                if result.get(x, y) == Color.MAGENTA.value:
                    mx, my = (x-y, 0)
                    for m in range(x+y + 1):
                        if mx >= 0:
                            result.set(mx, my, Color.MAGENTA.value)
                        mx += 1
                        my += 1
                else:
                    result.set(x, y, Color.BLUE.value)
        # plot_grids([result])
    return result

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py db695cfb blue_link") 
