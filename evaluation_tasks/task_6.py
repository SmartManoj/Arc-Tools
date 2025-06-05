from collections import Counter
from arc_tools import grid
from arc_tools.grid import Grid, detect_objects, Color, SubGrid, GridRegion, GridPoint
from arc_tools.plot import plot_grid, plot_grids
from arc_tools.logger import logger

def cropped_reflection_symmetry(grid: Grid) -> Grid:
    '''
    Fill the largest blue object with the equivalent symmetry region.
    This operates on a 30x30 grid (cropped from 32x32).
    '''
    blue_objects = detect_objects(grid, required_color=Color.LIGHTBLUE)
    blue_objects.sort(key=lambda x: x.width * x.height, reverse=True)
    blue_object_region = blue_objects[0].region

    for y in range(blue_object_region.y1, blue_object_region.y2 + 1):
        for x in range(blue_object_region.x1, blue_object_region.x2 + 1):
            for new_x, new_y in [
                (x, 31 - y), 
                (31 - x, y), 
                (31 - x, 31 - y), 
                (y, x), 
                (y, 31 - x), 
                (31 - y, x), 
                (31 - y, 31 - x), 
            ]:
                if 0 <= new_x < grid.width and 0 <= new_y < grid.height and grid[new_y][new_x] != Color.LIGHTBLUE.value:
                    grid[y][x] = grid[new_y][new_x]
                    break
    return SubGrid(blue_object_region, grid)

if __name__ == "__main__":
    import os
    os.system("main.py 0934a4d8 cropped_reflection_symmetry")