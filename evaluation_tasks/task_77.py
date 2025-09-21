import os
from arc_tools.grid import Color, Grid, SubGrid, detect_objects
from arc_tools import logger
from arc_tools.plot import plot_grids

def cropped_reflection_symmetry_v2(grid: Grid) -> Grid:
    '''
    Fill the largest black object with the equivalent symmetry region.
    This operates on a 30x30 grid (cropped from 32x32).
    '''
    black_objects = detect_objects(grid, required_color=Color.BLACK)
    black_objects.sort(key=lambda x: x.width * x.height, reverse=True)
    black_object_region = black_objects[0].region

    for y in range(black_object_region.y1, black_object_region.y2 + 1):
        for x in range(black_object_region.x1, black_object_region.x2 + 1):
            for new_x, new_y in [
                (x, 31 - y), 
                (31 - x, y), 
                (31 - x, 31 - y), 
                (y, x), 
                (y, 31 - x), 
                (31 - y, x), 
                (31 - y, 31 - x), 
            ]:
                if 0 <= new_x < grid.width and 0 <= new_y < grid.height and grid[new_y][new_x] != Color.BLACK.value:
                    grid[y][x] = grid[new_y][new_x]
                    break
    return SubGrid(black_object_region, grid)

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 981571dc cropped_reflection_symmetry_v2") 
