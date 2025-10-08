import os
from arc_tools.grid import Grid, detect_objects, Color
from arc_tools import logger
from arc_tools.plot import plot_grids

def expand(grid: Grid):
    '''
    Transform nested square pattern into starburst pattern where each 3x3 block is mirrored outside.
    The input has a 9x9 nested square pattern.
    '''
    obj = detect_objects(grid)[0]
    block_mappings = [
        # (input_start_row, input_start_col, output_start_row, output_start_col, rotate_180)
        (3, 3, 0, 0),  
        (3, 6, 0, 6),  
        (3, 9, 0, 12), 
        (6, 3, 6, 0),
        (6, 9, 6, 12),
        (9, 3, 12, 0), 
        (9, 6, 12, 6), 
        (9, 9, 12, 12),
    ]
    
    for input_row, input_col, output_row, output_col in block_mappings:
        for block_row in range(3):
            for block_col in range(3):
                source_row = input_row + block_row - 3 + obj.region.y1 
                source_col = input_col + block_col - 3 + obj.region.x1
                
                # Rotate 180 degrees: (2-row, 2-col)
                target_row = output_row + (2 - block_row) - 3 + obj.region.y1
                target_col = output_col + (2 - block_col) - 3 + obj.region.x1
               
                if (0 <= source_row < grid.height and 0 <= source_col < grid.width and
                    0 <= target_row < grid.height and 0 <= target_col < grid.width):
                    grid[target_row][target_col] = grid[source_row][source_col]

    x, y = obj.region.start                
    grid[y+3][x+3] = grid[y+2][x+2]
    grid[y+3][x+4] = grid[y+2][x+4]
    grid[y+3][x+5] = grid[y+2][x+6]
    
    grid[y+4][x+3] = grid[y+4][x+2]
    grid[y+4][x+4] = grid[y+2][x+3]
    grid[y+4][x+5] = grid[y+4][x+6]

    grid[y+5][x+3] = grid[y+6][x+2]
    grid[y+5][x+4] = grid[y+6][x+4]
    grid[y+5][x+5] = grid[y+6][x+6]
    return grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py db0c5428 expand") 
