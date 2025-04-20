import json
import os
from arc_tools import logger
from arc_tools.grid import Color, Grid, SubGrid, copy_object, detect_objects, rotate_object, GridRegion, GridPoint, flip_horizontally, move_object, place_object, rotate_object_counter_clockwise
from arc_tools.plot import plot_grid, plot_grids
import numpy as np
# logger.setLevel(10)

def is_hollow(obj: SubGrid) -> bool:
    """Check if a square has any holes in it."""
    
    for row in range(obj.region.height):
        for col in range(obj.region.width):
            if obj[row][col] == obj.parent_grid.background_color:      
                return True
    return False

def sort_by_size(grid: Grid):
    """ 
    stack holed squares on left side and remaining on right side.
    """
    # Detect all objects
    objects = detect_objects(grid)
    
    # Separate hollow and solid squares
    hollow_squares = []
    solid_squares = []
    
    for obj in objects:
        if is_hollow(obj):
            hollow_squares.append(obj)
        else:
            solid_squares.append(obj)
    
    # Create output grid
    max_pairs = max(len(hollow_squares), len(solid_squares))
    output_height = max_pairs * 4  # Each square is 4x4
    output_width = 8  # Two squares side by side
    output = Grid([[0] * output_width for _ in range(output_height)])
    
    # Place squares in output grid
    for i in range(max_pairs):
        # Place hollow square if available
        if i < len(hollow_squares):
            hollow = hollow_squares[i]
            place_object(hollow, 0, i*4, output)
        
        # Place solid square if available
        if i < len(solid_squares):
            solid = solid_squares[i]
            place_object(solid, 4, i*4, output)
    
    return output

if __name__ == "__main__":
    # Set up environment
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 2ba387bc sort_by_size")