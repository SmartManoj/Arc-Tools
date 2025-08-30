import os
from arc_tools.grid import Grid

def is_valid_rope(grid: Grid, line):
    """
    Check if a line is a valid rope (no branching points).
    Each point except endpoints should have exactly 2 connections.
    """
    connections_list = []
    for i, (col, row) in enumerate(line):
        # Count connections to this point
        connections = 0
        
        # Check all 8 directions around this point
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if (0 <= nr < grid.height and 0 <= nc < grid.width and 
                    grid[nr][nc] != grid.background_color):
                    connections += 1
        
        # For endpoints, we expect 1 connection (to the next/prev point in line)
        # For middle points, we expect 2 connections (to prev and next points)
        if len(line) == 2:
            connections_list.append(connections)
        if i not in [0, len(line) - 1]:
            if connections != 2:
                return False
    if len(line) == 2:
        # if any end has one connection, return False
        if not any(connection == 1 for connection in connections_list):
            return False
    return True

def broken_rope(grid: Grid):
    '''
    Analyze each diagonal line (rope) and determine if it can be tied horizontally/vertically or should be removed.
    '''
    # Get grid dimensions
    height, width = grid.height, grid.width
    
    # Find all diagonal lines
    diagonal_lines = []
    visited = set()  # Track visited cells to avoid overlaps
    
    # Find diagonal lines (down-right) of length 3+
    for row in range(height):
        for col in range(width):
            if grid[row][col] != grid.background_color and (col, row) not in visited:
                line = [(col, row)]
                c, r = col + 1, row + 1
                
                # Follow the diagonal
                while c < width and r < height and grid[r][c] != grid.background_color:
                    line.append((c, r))
                    c += 1
                    r += 1
                
                if len(line) >= 2:
                    # Validate that this is a proper rope (no branching)
                    if is_valid_rope(grid, line):
                        diagonal_lines.append(('down_right', line))
                        # Mark all cells in this rope as visited
                        for col, row in line:
                            visited.add((col, row))
    
    # Find diagonal lines (up-right) of length 3+
    for row in reversed(range(height)):
        for col in reversed(range(width)):
            if grid[row][col] != grid.background_color and (col, row) not in visited:
                line = [(col, row)]
                c, r = col + 1, row - 1
                
                # Follow the diagonal
                while c < width and r >= 0 and grid[r][c] != grid.background_color:
                    line.append((c, r))
                    c += 1
                    r -= 1
                
                if len(line) >= 2:
                    # Validate that this is a proper rope (no branching)
                    if is_valid_rope(grid, line):
                        diagonal_lines.append(('up_right', line))
                        # Mark all cells in this rope as visited
                        for col, row in line:
                            visited.add((col, row))
    
    # Create output grid - copy input
    output_grid = grid.copy()

    # Analyze each diagonal line (rope)
    for i, (direction, line) in enumerate(diagonal_lines, 1):
        rope_color = grid[line[0][1]][line[0][0]]

        
        # Check if rope is hanging by looking at endpoints
        start_point = line[0]
        end_point = line[-1]
        
        # Check if there are cells at the endpoints to anchor the rope
        start_anchored = False
        end_anchored = False
        
        # Check for horizontal/vertical connections at start point
        start_col, start_row = start_point
        if (start_col > 0 and grid[start_row][start_col-1] != grid.background_color) or \
           (start_col < width-1 and grid[start_row][start_col+1] != grid.background_color) or \
           (start_row > 0 and grid[start_row-1][start_col] != grid.background_color) or \
           (start_row < height-1 and grid[start_row+1][start_col] != grid.background_color):
            start_anchored = True
        
        # Check for horizontal/vertical connections at end point
        end_col, end_row = end_point
        if (end_col > 0 and grid[end_row][end_col-1] != grid.background_color) or \
           (end_col < width-1 and grid[end_row][end_col+1] != grid.background_color) or \
           (end_row > 0 and grid[end_row-1][end_col] != grid.background_color) or \
           (end_row < height-1 and grid[end_row+1][end_col] != grid.background_color):
            end_anchored = True
        

        
        # Check if rope can be tied horizontally or vertically
        can_tie_horizontal = False
        can_tie_vertical = False
        
        # Check if end point has horizontal connection
        end_col, end_row = end_point
        start_col, start_row = start_point
        if (end_col > 0 and grid[end_row][end_col-1] != grid.background_color) or \
           (end_col < width-1 and grid[end_row][end_col+1] != grid.background_color) or \
           (start_col > 0 and grid[start_row][start_col-1] != grid.background_color) or \
           (start_col < width-1 and grid[start_row][start_col+1] != grid.background_color):
            can_tie_horizontal = True
        
        # Check if end point has vertical connection  
        if (end_row > 0 and grid[end_row-1][end_col] != grid.background_color) or \
           (end_row < height-1 and grid[end_row+1][end_col] != grid.background_color) or \
           (start_row > 0 and grid[start_row-1][start_col] != grid.background_color) or \
           (start_row < height-1 and grid[start_row+1][start_col] != grid.background_color):
            can_tie_vertical = True
        
        # If rope is hanging (not anchored at either end), remove it
        if not start_anchored and not end_anchored:
            for col, row in line:
                output_grid[row][col] = output_grid.background_color
        if can_tie_horizontal:
            # Remove diagonal rope
            for col, row in line:
                output_grid[row][col] = output_grid.background_color
            # Add horizontal line, prefer anchored end
            start_col, start_row = line[0]
            end_col, end_row = line[-1]
            min_col = min(start_col, end_col)
            max_col = max(start_col, end_col)
            
            # Choose tie point based on which end is anchored
            if end_anchored:
                tie_row = end_row
            else:
                tie_row = start_row
            
            # Check if we can stretch in both directions - need anchors at the exact stretch positions
            can_stretch_left = (min_col > 0 and 
                              ((tie_row > 0 and grid[tie_row-1][min_col-1] != grid.background_color) or
                               (tie_row < height-1 and grid[tie_row+1][min_col-1] != grid.background_color)))
            can_stretch_right = (max_col < width-1 and 
                               ((tie_row > 0 and grid[tie_row-1][max_col+1] != grid.background_color) or
                                (tie_row < height-1 and grid[tie_row+1][max_col+1] != grid.background_color)))
            
            # Check if there are anchors at the end positions of the stretch
            # For horizontal stretch, we need anchors at the final positions where the rope would end
            stretch_left_end = min_col - 1
            stretch_right_end = max_col + 1
            has_anchor_at_stretch_left = (stretch_left_end >= 0 and 
                                        (grid[tie_row][stretch_left_end] != grid.background_color))
            has_anchor_at_stretch_right = (stretch_right_end < width and 
                                         (grid[tie_row][stretch_right_end] != grid.background_color))
            
            if has_anchor_at_stretch_left or has_anchor_at_stretch_right:
                # Stretch by 1 extra cell in both directions
                for col in range(min_col - 1, max_col + 2):  # -1 and +2 to add 1 extra cell on each side
                    if 0 <= col < width:
                        output_grid[tie_row][col] = rope_color
        if can_tie_vertical:
            # Remove diagonal rope
            for col, row in line:
                output_grid[row][col] = output_grid.background_color
            # Add vertical line, prefer anchored end
            start_col, start_row = line[0]
            end_col, end_row = line[-1]
            min_row = min(start_row, end_row)
            max_row = max(start_row, end_row)
            
            # Choose tie point based on which end is anchored
            if end_anchored:
                tie_col = end_col
            else:
                tie_col = start_col
            
            # Check if we can stretch in both directions - need anchors at the exact stretch positions
            can_stretch_up = (min_row > 0 and 
                            (grid[min_row-1][tie_col] != grid.background_color))
            can_stretch_down = (max_row < height-1 and 
                              (grid[max_row+1][tie_col] != grid.background_color))
            
            # Check if there are anchors at the end positions of the stretch
            # For vertical stretch, we need anchors at the final positions where the rope would end
            stretch_up_end = min_row - 1
            stretch_down_end = max_row + 1
            has_anchor_at_stretch_up = (stretch_up_end >= 0 and 
                                      (grid[stretch_up_end][tie_col] != grid.background_color))
            has_anchor_at_stretch_down = (stretch_down_end < height and 
                                        (grid[stretch_down_end][tie_col] != grid.background_color))
            
            # Check if there are anchors at the exact end positions where the rope would be placed
            # For vertical rope, check if there are anchors at the final rope positions
            rope_up_end = min_row - 1
            rope_down_end = max_row + 1
            has_anchor_at_rope_up = (rope_up_end >= 0 and 
                                   (grid[rope_up_end][tie_col] != grid.background_color))
            has_anchor_at_rope_down = (rope_down_end < height and 
                                     (grid[rope_down_end][tie_col] != grid.background_color))
            
            # Check if there are anchors at the positions where the rope would end after stretching
            # For vertical rope, check if there are anchors at the final rope positions
            rope_up_pole = min_row - 2
            rope_down_pole = max_row + 2
            has_anchor_at_final_up = (rope_up_pole >= 0 and 
                                    ( grid[rope_up_pole][tie_col] != grid.background_color))
            has_anchor_at_final_down = (rope_down_pole < height and 
                                      grid[rope_down_pole][tie_col] != grid.background_color)
            
            if not has_anchor_at_final_up and not has_anchor_at_final_down:
                has_anchor_at_rope_up = False
                has_anchor_at_rope_down = False
            
            if has_anchor_at_rope_up or has_anchor_at_rope_down:
                # Stretch by 1 extra cell in both directions
                for row in range(min_row - 1, max_row + 2):  # -1 and +2 to add 1 extra cell on each side
                    if 0 <= row < height:
                        output_grid[row][tie_col] = rope_color
    
    return output_grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 7b80bb43 broken_rope") 