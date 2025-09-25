import os
from arc_tools.constants import EIGHT_DIRECTIONS
from arc_tools.grid import Grid, detect_objects,Color
from arc_tools import logger
from arc_tools.plot import plot_grids

def border_n_fill(grid: Grid):
    '''
    Transform blue shapes: make them light blue if it has hollow, add red outline, 
    and fill hollow shapes' empty spaces with magenta.
    '''
    objects = detect_objects(grid)
    
    # Process each object
    for obj in objects:
        is_hollow = obj.get_holes_count() > 0
        
        if is_hollow:
            obj.replace_color(Color.BLUE,Color.LIGHT_BLUE)
            _fill_hollow_with_magenta(obj, grid)
        
        for point in obj.points:
            for dr, dc in EIGHT_DIRECTIONS:
                nr, nc = point.y + dr, point.x + dc
                if (0 <= nr < grid.height and 0 <= nc < grid.width and 
                    grid[nr][nc] == grid.background_color):
                    grid[nr][nc] = Color.RED.value
    
    return grid

def _fill_hollow_with_magenta(obj, grid):
    """Fill hollow spaces of object with magenta."""
    # Get bounding box
    min_row = min(point.y for point in obj.points)
    max_row = max(point.y for point in obj.points)
    min_col = min(point.x for point in obj.points)
    max_col = max(point.x for point in obj.points)
    
    # Fill background color cells inside with magenta, but only if they are
    # completely surrounded by object points (truly interior cells)
    for row in range(min_row + 1, max_row):
        for col in range(min_col + 1, max_col):
            if (not any(point.y == row and point.x == col for point in obj.points) and 
                grid[row][col] == grid.background_color):
                # Check if this cell is surrounded by object points on all 4 sides
                has_left = any(point.y == row and point.x < col for point in obj.points)
                has_right = any(point.y == row and point.x > col for point in obj.points)
                has_top = any(point.y < row and point.x == col for point in obj.points)
                has_bottom = any(point.y > row and point.x == col for point in obj.points)
                
                if has_left and has_right and has_top and has_bottom:
                    grid[row][col] = Color.MAGENTA.value


if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py aa4ec2a5 border_n_fill") 
