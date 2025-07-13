import json
from arc_tools import logger
from arc_tools.grid import Color, Grid, SubGrid, detect_objects, GridRegion, GridPoint, flip_horizontally, move_object
from arc_tools.plot import plot_grids
# logger.setLevel(10)

def update_fuel(obj: SubGrid, distance: int, orientation: str):
    if orientation == 'top':
        for row in range(obj.height):
            for col in range(obj.width):
                if obj[row][col] == Color.LIGHTGRAY.value:
                    obj[row][col] = Color.ORANGE.value
                    distance -= 1
                    if distance == 0:
                        return
    elif orientation == 'bottom':
        for row in reversed(range(obj.height)):
            for col in reversed(range(obj.width)):
                if obj[row][col] == Color.LIGHTGRAY.value:
                    obj[row][col] = Color.ORANGE.value
                    distance -= 1
                    if distance == 0:
                        return
    elif orientation == 'left':
        # start_x, start_y = 1, obj.height - 1
        for col in range(obj.width):
            for row in reversed(range(obj.height)):
                if obj[row][col] == Color.LIGHTGRAY.value:
                    obj[row][col] = Color.ORANGE.value
                    distance -= 1
                    if distance == 0:
                        return
    elif orientation == 'right':
        for col in reversed(range(obj.width)):
            for row in range(obj.height):
                if obj[row][col] == Color.LIGHTGRAY.value:
                    obj[row][col] = Color.ORANGE.value
                    distance -= 1
                    if distance == 0:
                        return


def move_rocket(obj: SubGrid):
    grid = obj.parent_grid
    x1, y1 = obj.region.x1, obj.region.y1
    x2, y2 = obj.region.x2, obj.region.y2

    # Count grey squares to determine max movement
    max_steps = obj.get_values_count()[Color.LIGHTGRAY.value]
    if max_steps == 0:
        return
    
    # check top
    if grid[y1 - 1][x1] == Color.MAROON.value:
        orientation = 'top'
        obj = obj.new_region(dy1 = -1)
        distance = 0
        for i in reversed(range(0, y1 - 1)):
            distance += 1
            if grid[i][x1] == Color.MAROON.value or distance == max_steps:
                break
        dx, dy = 0, -distance

    # check bottom
    if grid[y2 + 1][x2] == Color.MAROON.value:
        orientation = 'bottom'
        obj = obj.new_region(dy2 = 1)
        distance = 0
        for i in range(y2 + 2, grid.height):
            distance += 1
            if grid[i][x2] == Color.MAROON.value or distance == max_steps:
                break
        dx, dy = 0, distance

    # check left
    if grid[y1][x1 - 1] == Color.MAROON.value:
        orientation = 'left'
        obj = obj.new_region(dx1 = -1)
        distance = 0
        for i in reversed(range(0, x1 - 1)):
            distance += 1
            if grid[y1][i] == Color.MAROON.value or distance == max_steps:
                break
        dx, dy = -distance, 0

    # check right
    if grid[y2][x2 + 1] == Color.MAROON.value:
        orientation = 'right'
        obj = obj.new_region(dx2 = 1)
        distance = 0
        for i in range(x2 + 2, grid.width):
            distance += 1
            if grid[y2][i] == Color.MAROON.value or distance == max_steps:
                break
        dx, dy = distance, 0
    

    update_fuel(obj, distance, orientation)
    move_object(obj, dx, dy, grid)

def launch_rocket(grid: Grid) -> Grid:
    """ 
    Magenta is the background color.
    Maroon line is the wall.
    Rocket structure - nose-cone (maroon straight line) and fuel tank (black border box)
    Grey dots are the fuel.
    For each step, grey dot is replaced with orange dot.
    The rocket should touch the wall.
    """
    grid.background_color = Color.MAGENTA.value

    rocket_tanks = detect_objects(grid, ignore_color=Color.MAROON)
    for tank in rocket_tanks:
        move_rocket(tank)

    return grid

if __name__ == "__main__":
    import os
    os.environ['initial_file'] = __file__.split('.')[0]
    os.system("main.py 271d71e2 launch_rocket")