import os
from arc_tools.grid import Grid, detect_objects, Color
from arc_tools import logger
from arc_tools.plot import plot_grids

def army(grid: Grid):
    '''
    background color is blue
    queens are black color obj (max 3*3)
    surround the queens with orange color.
    remove single background color.
    '''
    grid.background_color = Color.BLUE.value
    objects = detect_objects(grid)
    backup_grid = grid.copy()
    queens = [obj for obj in objects if obj.color == Color.BLACK.value and obj.area <= 9]
    # remove blue count if it is surround by 5 black dots
    for row in range(grid.height):
        for col in range(grid.width):
            if grid.is_solo(row, col):
                if grid[row][col] == Color.BLUE.value:
                    grid[row][col] = Color.BLACK.value
    black_objects = detect_objects(grid, required_color=Color.BLACK, single_color_only=True)
    # sort
    black_objects.sort(key=lambda x: x.width, reverse=True)
    max_width = black_objects[0].width
    # skip those
    black_objects = [obj for obj in black_objects if obj.width != max_width]
    for obj in black_objects:
        # surround the queen with orange color
        for point in obj.points:
            for i in range(point.x - 1, point.x + 2):
                for j in range(point.y - 1, point.y + 2): 
                    if i >= 0 and i < grid.height and j >= 0 and j < grid.width:
                        if grid[j][i] == Color.BLUE.value: 
                            grid[j][i] =  Color.ORANGE.value
        
    for row in range(grid.height):
        for col in range(grid.width):
            if grid.is_solo(row, col):
                if grid[row][col] == Color.BLACK.value:
                    for i in range(row - 1, row + 2):
                        is_edge = all(grid[i][k] in [Color.BLACK.value] for k in range(col - 1, col + 2))
                        for j in range(col - 1, col + 2): 
                                if i >= 0 and i < grid.height and j >= 0 and j < grid.width:
                                    if grid[i][j] == Color.BLUE.value or is_edge: 
                                        grid[i][j] =  Color.ORANGE.value
                    

    return grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 71e489b6 army") 
