import json
from arc_tools import logger
from arc_tools.grid import Color, Grid, SubGrid, detect_objects, rotate_object, GridRegion, GridPoint, flip_horizontally, move_object
from arc_tools.plot import plot_grid, plot_grids
# logger.setLevel(10)
def move_drop(grid: Grid, point: GridPoint, direction: str) -> Grid:
    logger.info(f"Moving {grid[point.y][point.x]} from {point} to {direction}")
    if direction == 'left':
        for x in range(point.x-1, -1, -1):
            # go down until non background color
            for y in range(point.y, grid.height-1):
                if grid[y+1][x] != grid.background_color:
                    if x > 1 and grid[y][x - 1] == grid.background_color:
                        return move_drop(grid, GridPoint(x, y), 'left')
                    logger.info(f"Moving {grid[point.y][point.x]} from {point} to {GridPoint(x, y)}")
                    grid[y][x] = Color.BLUE.value
                    return grid
            
    elif direction == 'right':
        move_object(grid, point, GridPoint(point.x+1, point.y))
    return grid

def flow_water(grid: Grid) -> Grid:
    """ 
    water should flow from top to bottom
    """
    # Create a new grid with the same dimensions as input
    # (8, 1) should come to (6, 8)

    for y in reversed(range(grid.height)):
        for x in range(1, grid.width):
            while grid[y][x] == Color.BLUE.value and grid[y][x-1] == grid.background_color:
                # shift above dots
                for y2 in reversed(range(1,y + 1)):
                    if grid[y2][x] == grid.background_color:
                        break
                    grid[y2][x] = grid[y2-1][x]

                grid[0][x] = grid.background_color

                move_drop(grid, GridPoint(x, y), 'left')
    
    
    plot_grid(grid, show=True)
    return grid

if __name__ == "__main__":
    import os
    os.environ['initial_file'] = __file__.split('.')[0]
    os.system("python main.py 28a6681f flow_water")