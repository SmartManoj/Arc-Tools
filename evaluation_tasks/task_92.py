import os
from textwrap import fill
from arc_tools.grid import Grid, detect_objects, Color
from arc_tools import logger
from arc_tools.plot import plot_grids

def consistency(grid: Grid):
    '''
    Copy the pattern from the edge that has non-zero values upward/downward/leftward/rightward.
    The pattern is: copy the edge row/column, but if the last color differs from the first color,
    use the last color as a hint for what the first color should become.
    '''
    result = grid.copy()
    
    # Check which edge has non-zero values
    if any(i.value != grid.background_color for i in grid.get_edge_points('left')):
        start_direction = 'left'
    elif any(i.value != grid.background_color for i in grid.get_edge_points('right')):
        start_direction = 'right'
    elif any(i.value != grid.background_color for i in grid.get_edge_points('top')):
        start_direction = 'top'
    elif any(i.value != grid.background_color for i in grid.get_edge_points('bottom')):
        start_direction = 'bottom'
    else:
        return result  # No edge has non-zero values
    
    
    if start_direction == 'top':
        # Process each column independently from top to bottom
        for col in range(grid.width):
            positions = []
            colors = []
            for row in range(grid.height):  # Start from top
                if grid[row][col] != grid.background_color:
                    positions.append(row)
                    colors.append(grid[row][col])
            if len(positions) < 2: continue
            gap = abs(positions[0] - positions[1])
            fill_color = colors[0]
            
            if have_fill_color := (len(positions) == 3 and (positions[-1] - positions[0])%gap == 0):
                fill_color = colors[-1]
            for row in range(positions[0], grid.height, gap):
                if have_fill_color and result[row][col] == fill_color:
                    break
                else:
                    result[row][col] = fill_color
    
    elif start_direction == 'bottom':
        # Process each column independently from bottom to top
        for col in range(grid.width):
            positions = []
            colors = []
            for row in range(grid.height - 1, -1, -1):  # Start from bottom
                if grid[row][col] != grid.background_color:
                    positions.append(row)
                    colors.append(grid[row][col])
            if len(positions) < 2: continue
            gap = abs(positions[0] - positions[1])
            fill_color = colors[0]
            
            if have_fill_color := (len(positions) == 3 and (positions[-1] - positions[0])%gap == 0):
                fill_color = colors[-1]
            for row in range(positions[0], -1, -gap):
                if have_fill_color and result[row][col] == fill_color:
                    break
                else:
                    result[row][col] = fill_color
    
    elif start_direction == 'left':
        # Process each row independently from left to right
        for row in range(grid.height):
            positions = []
            colors = []
            for col in range(grid.width):  # Start from left
                if grid[row][col] != grid.background_color:
                    positions.append(col)
                    colors.append(grid[row][col])
            if len(positions) < 2: continue
            gap = abs(positions[0] - positions[1])
            fill_color = colors[0]
            
            if have_fill_color := (len(positions) == 3 and (positions[-1] - positions[0])%gap == 0):
                fill_color = colors[-1]
            for col in range(positions[0], grid.width, gap):
                if have_fill_color and result[row][col] == fill_color:
                    break
                else:
                    result[row][col] = fill_color
    
    elif start_direction == 'right':
        # Process each row independently from right to left
        for row in range(grid.height):
            positions = []
            colors = []
            for col in range(grid.width - 1, -1, -1):  # Start from right
                if grid[row][col] != grid.background_color:
                    positions.append(col)
                    colors.append(grid[row][col])
            if len(positions) < 2: continue
            gap = abs(positions[0] - positions[1])
            fill_color = colors[0]
            
            if have_fill_color := (len(positions) == 3 and (positions[-1] - positions[0])%gap == 0):
                fill_color = colors[-1]
            for col in range(positions[0], -1, -gap):
                if have_fill_color and result[row][col] == fill_color:
                    break
                else:
                    result[row][col] = fill_color
  
        
    return result

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 16de56c4 consistency") 