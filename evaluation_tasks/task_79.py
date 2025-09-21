import os
from arc_tools.grid import Color, Grid, detect_objects
from arc_tools import logger
from arc_tools.plot import plot_grids

def go_thru_right_path(grid: Grid):
    '''
    rose dot on left edge go through the path if it is same color on both sides
    '''
    # Color mapping: 6 = magenta, 7 = pink
    MAGENTA = Color.MAGENTA.value
    
    result = grid.copy()
    # Process each row
    for initial_row in range(1, grid.height - 1):
        col = 0
        row = initial_row
        # check for eligibility
        # fast forward to the first non-background color
        eligible = False
        for col in range(1, grid.width):
            p = grid[row-1][col]
            c = grid[row][col]
            n = grid[row+1][col]
            if not (p == c == n == grid.background_color):
                if p == n and c == grid.background_color:
                    eligible = True
                break
        if eligible:
            steps = 0
            direction = 'right'
            while steps < 160:
                steps += 1
                if col == grid.width:
                    col -= 1
                    break
                if direction == 'right':
                    p = grid[row-1][col+1]
                    n = grid[row+1][col+1]
                    if (1 or p == n or grid.background_color in [p, n]) and grid[row][col+1] == grid.background_color:
                        col += 1
                        if col == grid.width - 1:
                            break
                    else:
                        if grid[row][col+1] != grid.background_color:
                            if grid[row-1][col] == grid.background_color:
                                direction = 'up'    
                            else:
                                direction = 'down'
                elif direction == 'down':
                    l = grid[row+1][col - 1]
                    r = grid[row+1][col+1]
                    if (1 or l == r or grid.background_color in [l, r]) and grid[row+1][col] == grid.background_color:
                        row += 1
                        if row == grid.height - 1:
                            break
                    else:
                        if grid[row+1][col] != grid.background_color:
                            if grid[row][col-1] == grid.background_color and grid[row-1][col-1] == grid[row+1][col-1]:
                                direction = 'left'
                            elif grid[row][col+1] == grid.background_color and grid[row-1][col+1] == grid[row+1][col+1]:
                                direction = 'right'
                            else:
                                break
                elif direction == 'left':
                    if (1 or grid[row+1][col-1] == grid[row-1][col-1] or grid.background_color in [grid[row+1][col-1], grid[row-1][col-1]]) and grid[row][col-1] == grid.background_color:
                        col -= 1
                        if col == 0:
                            break
                    else:
                        break
                elif direction == 'up':
                    l = grid[row-1][col-1]
                    r = grid[row-1][col+1]
                    if (1 or l == r or grid.background_color in [l, r]) and grid[row - 1][col] == grid.background_color:
                        row -= 1
                        if row == 0:
                            break
                    else:
                        direction = 'right'
            result[row][col] = MAGENTA
            result[initial_row][0] = grid.background_color
    return result

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 9bbf930d go_thru_right_path") 