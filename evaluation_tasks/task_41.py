import os
from collections import Counter
from arc_tools.grid import Color, Grid, SubGrid, detect_objects, GridRegion, GridPoint, copy_object
from arc_tools import logger
from arc_tools.plot import plot_grids

def align_the_stars(grid: Grid):
    '''
    star marks will be placed on the edge of the grid.
    move the stars vertically or horizontally to align with the star marks.
    '''
    # Create a copy of the grid to work with
    result_grid = grid.copy()
    
    # Detect all objects in the grid
    objects = detect_objects(grid)
    
    star_objects = []
    star_marks = []
    
    for obj in objects:
        if obj.width == 1 and obj.height == 1:
            # Only consider single cells on the edges as marks
            y, x = obj.region.y1, obj.region.x1
            if y == 0 or y == grid.height - 1 or x == 0 or x == grid.width - 1:
                star_marks.append(obj)
            else:
                # Single cell not on edge, treat as part of a larger object
                star_objects.append(obj)
        else:
            star_objects.append(obj)
    
    # Clear all star objects from the result grid
    for obj in star_objects:
        result_grid.remove_object(obj)
    
    # Process each mark and find objects that should align to it
    for mark in star_marks:
        mark_color = mark.color
        mark_y = mark.region.y1
        mark_x = mark.region.x1
        
        # Find objects that contain this mark's color and haven't been processed
        for obj in star_objects:
                
            # Check if this object contains the mark color
            mark_position = None
            for row in range(obj.height):
                for col in range(obj.width):
                    # mark color should be the only once in the object
                    if obj[row][col] == mark_color and obj.get_values_count()[mark_color] == 1:
                        mark_position = (row, col)
                        break
                if mark_position:
                    break
            
            if mark_position:
                obj_row, obj_col = mark_position
                current_mark_y = obj.region.y1 + obj_row
                current_mark_x = obj.region.x1 + obj_col
                
                # Determine alignment based on mark position
                if mark_x == 0 or mark_x == grid.width - 1:
                    dy = mark_y - current_mark_y
                    dx = 0
                else:
                    dx = mark_x - current_mark_x
                    dy = 0
                
                copy_object(obj, dx, dy, result_grid)
                
    
    return result_grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 581f7754 align_the_stars") 
