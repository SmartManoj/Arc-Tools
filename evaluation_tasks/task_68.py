from collections import Counter
import os
from arc_tools.grid import Color, Grid, detect_objects
from arc_tools import logger
from arc_tools.plot import plot_grid, plot_grids

def hole_counter(grid: Grid):
    '''
    Count how many holes in each frame, then create a summary grid.
    '''
    objects = detect_objects(grid)
    for obj in objects:
        if obj.area == 1:
            noise_color = obj.color
            break
    frame_chain = [obj for obj in objects if obj.area != 1 and obj.color != noise_color][0]
    frame_chain = Grid(frame_chain)
    # Get all unique colors except background
    unique_colors = [color for color in frame_chain.get_unique_values(sort=False) if color != frame_chain.background_color]
    
    # For each color, create an object containing only that color
    visited_objects = {}
    for color in unique_colors:
        # Create a copy of frame_chain with only the current color, rest as background
        color_grid = frame_chain.copy()
        for row in range(color_grid.height):
            for col in range(color_grid.width):
                if color_grid[row][col] != color:
                    color_grid[row][col] = frame_chain.background_color
        
        obj = color_grid
        visited_objects[color] = obj
        
        # Fill holes for this color object
        for row in range(obj.height):
            for col in range(obj.width):
                if obj[row][col] == grid.background_color:
                    if frame_chain[row][col] != grid.background_color:
                        
                        is_horizontal_gap = (col > 0 and col < obj.width-1 and 
                                           obj[row][col-1] == color and 
                                           obj[row][col+1] == color)
                        is_vertical_gap = (row > 0 and row < obj.height-1 and 
                                         obj[row-1][col] == color and 
                                         obj[row+1][col] == color)
                        surrounding_values = obj.get_surrounding_values(row, col)
                        is_noise = frame_chain[row][col] == noise_color
                        if ((is_horizontal_gap or is_vertical_gap) and surrounding_values.count(color) <= 4) or (is_noise and surrounding_values.count(color) <= 3):
                            obj[row][col] = color
    hole_counter = {}                        
    for color, obj in visited_objects.items():
        if color == noise_color:
            continue
        hole_counter[color] = obj.get_holes_count()
    cols = max(hole_counter.values())
    new_grid = Grid([[noise_color for _ in range(cols)] for _ in range(len(hole_counter))])
    grid_values = grid.get_unique_values()

    for y, (color, count) in enumerate(sorted(hole_counter.items(), key=lambda x: (x[1], grid_values.index(x[0])))):
        for x in range(count):
            new_grid[y][x] = color
    
    return new_grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 89565ca0 hole_counter") 
