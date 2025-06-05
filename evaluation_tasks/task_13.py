from collections import Counter
from arc_tools.grid import Grid, copy_object, detect_objects, Color, SubGrid, GridRegion, GridPoint, move_object, rotate_object
from arc_tools.plot import plot_grid, plot_grids
from arc_tools.logger import logger
import math

def tetris_pipe(grid: Grid) -> Grid:
    '''
    Find the blue Tetris pipe.
    The  center dot is the paint color.
    If it is blue, the surrounding dots are the new paint color.
    The touched region will be filled with the new paint color.
    If a brown L shape (3*3) is present, how should the grid be rotated ?.
    Remove the pipe and L shape.
    '''
    pipes = detect_objects(grid, required_color=Color.BLUE, max_count=4, single_color_only=True)
    # Get the center point of the first pipe object
    for pipe in pipes:
        width = pipe.width
        height = pipe.height
        if width > height:
            if pipe[0][0] == Color.BLUE.value:
                pipe.paint_color = pipe[0][1]
                surrounding_color = pipe[1][0]
                pipe.touch_color_point = GridPoint(pipe.region.x1 + 1, pipe.region.y1 + 2)
                if pipe.paint_color == Color.BLUE.value:
                    pipe.paint_color = surrounding_color
            else:
                pipe.paint_color = pipe[1][1]
                surrounding_color = pipe[0][0]
                pipe.touch_color_point = GridPoint(pipe.region.x1 + 1, pipe.region.y1 - 2)
                if pipe.paint_color == Color.BLUE.value:
                    pipe.paint_color = surrounding_color
        else:
            if pipe[0][0] == Color.BLUE.value:
                pipe.paint_color = pipe[1][0]
                surrounding_color = pipe[0][1]
                pipe.touch_color_point = GridPoint(pipe.region.x1 + 2, pipe.region.y1 + 1)
                if pipe.paint_color == Color.BLUE.value:
                    pipe.paint_color = surrounding_color
            else:
                pipe.paint_color = pipe[1][1]
                surrounding_color = pipe[0][0]
                pipe.touch_color_point = GridPoint(pipe.region.x1 - 2, pipe.region.y1 + 1)
                if pipe.paint_color == Color.BLUE.value:
                    pipe.paint_color = surrounding_color
        grid.remove_object(pipe, surrounding_color)
    # find L shape
    l_shapes = detect_objects(grid, required_color=Color.MAROON)
    number_of_rotations = 0
    if l_shapes:
        l_shape = l_shapes[0]
        four_corner_points = [
            GridPoint(l_shape.region.x2, l_shape.region.y1), 
            GridPoint(l_shape.region.x2, l_shape.region.y2),
            GridPoint(l_shape.region.x1, l_shape.region.y1), 
            GridPoint(l_shape.region.x1, l_shape.region.y2), 
        ]
        for k,point in enumerate(four_corner_points):
            if grid[point.y][point.x] != Color.MAROON.value:
                grid.remove_object(l_shape, grid[point.y][point.x])
                logger.info(f"number of rotations: {k}")
                number_of_rotations = k
                break
    # plot_grids([grid, *pipes], save_all=1, show=True)
    for pipe in pipes:
        grid.fill_color(pipe.touch_color_point, -pipe.paint_color)
    for pipe in pipes:
        grid.fill_color(pipe.touch_color_point, pipe.paint_color)
        # plot_grids([grid, pipe], save_all=1, show=True)
    for _ in range(number_of_rotations):
        grid = rotate_object(grid)
    return grid

if __name__ == "__main__":
    import os
    os.system("main.py 21897d95 tetris_pipe")