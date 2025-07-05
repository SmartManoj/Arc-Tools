import os
from collections import Counter
from arc_tools.grid import Color, Grid, SubGrid, detect_objects, GridRegion, GridPoint, place_object_on_new_grid
from arc_tools import logger
from arc_tools.plot import plot_grids

def laser_gun(grid: Grid):
    '''
    Creates vertical laser beams from isolated colored objects.
    Finds small isolated colored objects that act as laser guns
    and fires vertical beams based on blue handler position:
    - If blue handler is above the gun → fire downward from gun position
    - If blue handler is below the gun → fire upward from gun position
    '''
    result = grid.copy()
    
    # Find all blue (1) objects to identify handlers
    blue_objects = detect_objects(grid, required_color=Color.BLUE)
    blue_positions = set()
    for obj in blue_objects:
        for y in range(obj.region.y1, obj.region.y2 + 1):
            for x in range(obj.region.x1, obj.region.x2 + 1):
                if grid.get(x, y) == Color.BLUE.value:
                    blue_positions.add((x, y))
    
    # Find gun positions by looking for colored objects above or below handlers
    guns_by_column = {}  # column -> list of (row, color) tuples
    
    # Group blue handlers by column
    blue_by_column = {}
    for x, y in blue_positions:
        if x not in blue_by_column:
            blue_by_column[x] = []
        blue_by_column[x].append(y)
    
    # For each column with blue handlers, find guns above or below
    for blue_col, blue_rows in blue_by_column.items():
        blue_min_row = min(blue_rows)
        blue_max_row = max(blue_rows)
        
        # Look for colored objects in this column
        for y in range(blue_min_row - 2, blue_max_row + 3):
            current_color = grid.get(blue_col, y)
            # Skip background
            if current_color == grid.background_color:
                continue
            
            # Check if this colored object is within 2 rows above or below the blue handler
            if (blue_min_row - 2 <= y < blue_min_row) or (blue_max_row < y <= blue_max_row + 2):
                # This is a gun!
                if blue_col not in guns_by_column:
                    guns_by_column[blue_col] = []
                guns_by_column[blue_col].append((y, current_color))
    
    # Fire lasers from each gun column
    for gun_col, gun_data in guns_by_column.items():
        # Sort guns by row to get colors in vertical order
        gun_data.sort(key=lambda x: x[0])
        gun_colors = [color for row, color in gun_data]
        
        # Find blue handler position in this column
        blue_positions_in_column = [(x, y) for x, y in blue_positions if x == gun_col]
        
        # Get gun position range
        gun_min_row = min(row for row, color in gun_data)
        gun_max_row = max(row for row, color in gun_data)
        
        # Check if any blue handler is above the guns
        handler_above_gun = any(y < gun_min_row for x, y in blue_positions_in_column)
        
        if handler_above_gun:
            # Fire downward from gun position
            start_row = gun_max_row + 1
            
            # Fire laser downward until end of grid
            for y in range(start_row, grid.height):
                color_index = (y - start_row) % len(gun_colors)
                result.set(gun_col, y, gun_colors[color_index])
        else:
            # Fire upward from gun position
            end_row = gun_min_row - 1
            
            # Reverse colors for upward firing
            gun_colors.reverse()
            
            # Fire laser upward from gun position
            for y in range(end_row, -1, -1):
                color_index = (end_row - y) % len(gun_colors)
                result.set(gun_col, y, gun_colors[color_index])
    
    return result

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 53fb4810 laser_gun") 
