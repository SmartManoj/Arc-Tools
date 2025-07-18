import os
import copy
from collections import deque
from arc_tools.grid import Grid, Color, detect_objects

def make_red_regions(grid: Grid) -> Grid:
    """
    Fills the regions between parallel yellow diagonal walls with red.
    """
    output_grid = grid.copy()
    wall_color = grid.get_max_color()
    fill_color = Color.RED.value
    height, width = grid.height, grid.width

    for r in range(height):
        for c in range(width):
            if grid[r][c] == wall_color:
                continue

            # Check for enclosure by '/' diagonal walls by casting rays in the perpendicular '\' direction
            has_wall_top_left = False
            i, j = r - 1, c - 1
            while i >= 0 and j >= 0:
                if grid[i][j] == wall_color or (grid[i][j+1] == wall_color and grid[i+1][j] == wall_color):
                    has_wall_top_left = True
                    break
                i -= 1
                j -= 1

            has_wall_bottom_right = False
            i, j = r + 1, c + 1
            while i < height and j < width:

                if grid[i][j] == wall_color or (grid[i - 1][j] == wall_color and grid[i][j - 1] == wall_color):
                    has_wall_bottom_right = True
                    break
                i += 1
                j += 1

            if has_wall_top_left and has_wall_bottom_right:
                output_grid[r][c] = fill_color

    return output_grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 7666fa5d make_red_regions")
