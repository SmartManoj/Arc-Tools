import os
from arc_tools.grid import Grid, detect_objects, Color
from arc_tools import logger
from arc_tools.plot import plot_grids

def bottom_view(grid: Grid):
    '''
    Show the bottom view of crossed ropes.
    Remove red markers.
    Yellow markers indicate direction changes.
    '''
    result = grid.copy()
    red_dots = detect_objects(grid, required_colors=[Color.RED])
    for red_dot in red_dots:
        spv = grid.get_surrounding_points(red_dot.region.y1, red_dot.region.x1, ignore_corner=1)
        # filter yellow
        spv = [point for point in spv if point.value != Color.YELLOW.value]
        sp1v = spv[0].value
        result[red_dot.region.y1][red_dot.region.x1] = sp1v
    
    yellow_dots = detect_objects(result, required_colors=[Color.YELLOW])
    for yellow_dot in yellow_dots:
        x, y = yellow_dot.region.x1, yellow_dot.region.y1
        up1 = result[y - 1][x]
        up2 = result[y - 2][x]
        down1 = result[y + 1][x]
        down2 = result[y + 2][x]
        left1 = result[y][x - 1]
        left2 = result[y][x - 2]
        right1 = result[y][x + 1]
        right2 = result[y][x + 2]
        if left1 == left2 not in [grid.background_color, []]:
            for x1 in range(0, x-1):
                if result[y][x1] == left1:
                    result[y][x1] = grid.background_color
            result[y][x] = left1
            for x1 in range(x+1, grid.width):
                if result[y][x1] == grid.background_color:
                    result[y][x1] = left1
        elif up1 == up2 not in [grid.background_color, []]:
            for y1 in range(0, y-1):
                if result[y1][x] == up1:
                    result[y1][x] = grid.background_color
            for y1 in range(y, result.height):
                if result[y1][x] == grid.background_color:
                    result[y1][x] = up1
        elif right1 == right2 not in [grid.background_color, []]:
            for x1 in range(x+2, grid.width):
                if result[y][x1] == right1:
                    result[y][x1] = grid.background_color
                elif result[y][x1] == grid.background_color:
                    if result[y-1][x1-1] == right1:
                        for y1 in range(0, y):
                            result[y1][x1-1] = grid.background_color
                    elif result[y+1][x1-1] == right1:
                        for y1 in range(y, result.height):
                            result[y1][x1-1] = grid.background_color
                    break
            for x1 in range(0, x+1):
                result[y][x1] = right1

    priority_value = None
    for row in range(result.height):
        for col in range(result.width):
            cv = result[row][col]
            up = result[row - 1][col]
            down = result[row + 1][col]
            left = result[row][col - 1]
            right = result[row][col + 1]
            up_left = result[row - 1][col - 1]
            up_right = result[row - 1][col + 1]
            down_left = result[row + 1][col - 1]
            down_right = result[row + 1][col + 1]
            if up == down and left == right and up not in [grid.background_color, []] and left not in [grid.background_color, []]:
                if cv!=grid.background_color:
                    priority_value = up if up != cv else left
                    result[row][col] = priority_value
                else:
                    result[row][col] = priority_value if priority_value else left

            elif left == right and left not in [grid.background_color, []] and [up_left, down_left, up_right, down_right].count(left) < 2:
                result[row][col] = left
            elif up == down and up not in [grid.background_color, []] and [up_left, up_right, down_left, down_right].count(up) < 2:
                result[row][col] = up
    
    
    return result

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py faa9f03d bottom_view") 
