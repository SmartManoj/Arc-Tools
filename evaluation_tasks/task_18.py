import json
from arc_tools import logger
from arc_tools.grid import Color, Grid, SubGrid, detect_objects, rotate_object, GridRegion, GridPoint, flip_horizontally, move_object
from arc_tools.plot import plot_grid, plot_grids
# logger.setLevel(10)
def move_drop(grid: Grid, point: GridPoint, direction: str, previous_point: GridPoint = None) -> Grid:
    if direction == 'left':
        for x in range(point.x-1, -1, -1):
            # go down until non background color
            for y in range(point.y, grid.height):
                if y == grid.height - 1 or grid[y+1][x] != grid.background_color:
                    # Don't move back to previous position
                    if not (previous_point and x == previous_point.x and y == previous_point.y):
                        if x > 0 and grid[y][x - 1] == grid.background_color:
                            return move_drop(grid, GridPoint(x, y), 'left', point)
                        if x < grid.width-1 and grid[y][x + 1] == grid.background_color:
                            return move_drop(grid, GridPoint(x, y), 'right', point)
                    grid[y][x] = Color.BLUE.value
                    return GridPoint(x, y)
            
    else:
        for x in range(point.x+1, grid.width):
            # go down until non background color
            for y in range(point.y, grid.height):
                if y == grid.height - 1 or grid[y+1][x] != grid.background_color:
                    # Don't move back to previous position
                    if not (previous_point and x == previous_point.x and y == previous_point.y):
                        if x < grid.width-1 and grid[y][x + 1] == grid.background_color:
                            return move_drop(grid, GridPoint(x, y), 'right', point)
                        if x > 0 and grid[y][x - 1] == grid.background_color:
                            return move_drop(grid, GridPoint(x, y), 'left', point)
                    grid[y][x] = Color.BLUE.value
                    return GridPoint(x, y)


def flow_water(grid: Grid) -> Grid:
    """ 
    water should flow from top to bottom
    """
    for y in reversed(range(grid.height)):
        for x in list(range(grid.width)) + list(reversed(range(grid.width))):
            while grid[y][x] == Color.BLUE.value and any([v == grid.background_color for v in [grid[y][x-1], grid[y][x+1]]]):
                # shift above dots
                for y2 in reversed(range(1, y+1)):
                    grid[y2][x] = grid[y2-1][x]
                grid[0][x] = grid.background_color
                if grid[y][x-1] == grid.background_color:
                    new_point = move_drop(grid, GridPoint(x, y), 'left')
                else:
                    new_point = move_drop(grid, GridPoint(x, y), 'right')
                if new_point == GridPoint(x, y):
                    break
    return grid

if __name__ == "__main__":
    import os
    os.environ['initial_file'] = __file__.split('.')[0]
    os.system("python main.py 28a6681f flow_water")