import os
from arc_tools.grid import Grid, GridPoint, GridRegion, detect_objects, Color, place_object_on_new_grid
from arc_tools import logger
from arc_tools.plot import plot_grid, plot_grids

def role_model_v2(grid: Grid):
    '''
    hint region separtor - Magenta vertical line
    hints - box, shape, position, orientation
    put box based on shape, position and orientation

    '''
    pipes = [x for x in range(grid.width) if grid[0][x] == Color.MAGENTA.value]
    left_region = GridRegion([GridPoint(0, 0), GridPoint(pipes[0] - 1, grid.height-1)])
    left_grid = grid.crop(left_region)
    left_grid.background_color = Color.BLACK.value
    if len(pipes) == 1:
        right_grid = None
        pipes.append(grid.width)
    else:
        right_region = GridRegion([GridPoint(pipes[1] + 1, 0), GridPoint(grid.width - 1, grid.height-1)])
        right_grid = grid.crop(right_region)
        right_grid.background_color = Color.BLACK.value
        
    center_region = GridRegion([GridPoint(pipes[0] + 1, 0), GridPoint(pipes[1] - 1, grid.height-1)])
    center_grid = grid.crop(center_region)
    box, shape, position, orientation = detect_objects(left_grid, ignore_colors=[Color.MAGENTA])
    # swap shape colors
    box.swap_colors()
    x,y = orientation.region.start
    if orientation.width == 1:
        if grid[y-1][x] == 0:
            # botttom
            n = 2
        else:
            # top
            n = 0
    else:
        if grid[y][x-1] == 0:
            # right
            n = 1
        else:
            # left
            n = 3
    for _ in range(n):
        shape = shape.rotate()
    
    enlarged_shape_size = shape.width * box.width, shape.height * box.height
    # position.region
    x, y = position.region.start
    if grid[y+1][x+1] == 0:
        start_col, start_row = 0, 0
    elif grid[y+1][x-1] == 0:
        start_col, start_row = center_grid.width - enlarged_shape_size[0], 0
    elif grid[y-1][x+1] == 0:
        start_col, start_row = 0, center_grid.height - enlarged_shape_size[1]
    elif grid[y-1][x-1] == 0:
        start_col, start_row = center_grid.width - enlarged_shape_size[0], center_grid.height - enlarged_shape_size[1]
    # place box based on shape
    for row in range(shape.height):
        for col in range(shape.width):
            if shape[row][col] != 0:
                col1 = col  * box.width + start_col
                row1 = row * box.height + start_row
                place_object_on_new_grid(box, col1, row1  ,  center_grid)
    if right_grid:
        # Process right region similar to left region
        right_box, right_shape, right_position, right_orientation = detect_objects(right_grid, ignore_colors=[Color.MAGENTA])
        # swap shape colors
        right_box.swap_colors()
        x,y = right_orientation.region.start
        if right_orientation.width == 1:
            if grid[y-1][x] == 0:
                # botttom
                n = 2
            else:
                # top
                n = 0
        else:
            if grid[y][x-1] == 0:
                # right
                n = 1
            else:
                # left
                n = 3
        for _ in range(n):
            right_shape = right_shape.rotate()
        right_enlarged_shape_size = right_shape.width * right_box.width, right_shape.height * right_box.height
        # position.region
        rx, ry = right_position.region.start
        if grid[ry+1][rx+1] == 0:
            right_start_col, right_start_row = 0, 0
        elif grid[ry+1][rx-1] == 0:
            right_start_col, right_start_row = center_grid.width - right_enlarged_shape_size[0], 0
        elif grid[ry-1][rx+1] == 0:
            right_start_col, right_start_row = 0, center_grid.height - right_enlarged_shape_size[1]
        elif grid[ry-1][rx-1] == 0:
            right_start_col, right_start_row = center_grid.width - right_enlarged_shape_size[0], center_grid.height - right_enlarged_shape_size[1]
        # place box based on shape
        for row in range(right_shape.height):
            for col in range(right_shape.width):
                if right_shape[row][col] != 0:
                    col1 = col  * right_box.width + right_start_col
                    row1 = row * right_box.height + right_start_row
                    place_object_on_new_grid(right_box, col1, row1  ,  center_grid)
    return center_grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py a32d8b75 role_model_v2") 
