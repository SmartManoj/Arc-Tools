import os
from arc_tools.grid import Grid, detect_objects, Color
from arc_tools import logger
from arc_tools.plot import plot_grids
from collections import Counter

def bouncer(input_grid: Grid):
    '''
    Shoot rays from center square in 4 directions.
    When hitting colored blocks, side bounce based on color segment position and ray direction.
    Bounces can bounce again when hitting other blocks (recursive).
    '''
    # Parse color segments from top 5 rows
    segment_info = {}
    for col_start in [1, 7, 13, 19]:
        color, line_on_left = None, False
        for r in range(1, 5):
            for c in range(col_start, col_start + 4):
                if input_grid[r][c] not in [0, 5]:
                    if color is None:
                        color = input_grid[r][c]
                    if c == col_start:
                        line_on_left = True
        if color:
            segment_info[color] = 'left' if line_on_left else 'right'
    
    # Crop the grid - remove top 6 rows and work on cropped grid
    grid = Grid([[input_grid[r][c] for c in range(input_grid.width)] for r in range(6, input_grid.height)])
    
    gun = detect_objects(grid, required_colors=[Color.LIGHT_BLUE])[0]
    # Find center in cropped grid
    center_r, center_c = gun.region.y1, gun.region.x1
    gun_width = gun.region.width
    gun_height = gun.region.height
    
    # Get background color
    bg_counter = Counter()
    for r in range(grid.height):
        for c in range(grid.width):
            if grid[r][c] not in [8, 5, 0]:
                bg_counter[grid[r][c]] += 1
    bg_color = bg_counter.most_common(1)[0][0]
    
    def is_empty(r, c):
        """Check if cell is empty background"""
        if r < 0 or r >= grid.height or c < 0 or c >= grid.width:
            return False
        return grid[r][c] in [bg_color, Color.LIGHT_BLUE.value] 
    
    def draw_line(cells):
        """Draw cells as color 8, but don't overwrite colored blocks"""
        for r, c in cells:
            if 0 <= r < grid.height and 0 <= c < grid.width:
                # Don't overwrite colored blocks from segment_info
                if grid[r][c] not in segment_info:
                    grid[r][c] = 8
    
    def shoot_and_bounce(start_r, start_c, width, height, dr, dc, is_horizontal, bounce_depth=0, parent_direction=None):
        """
        Shoot a multi-cell wide ray/bounce and handle recursive bouncing.
        start_r, start_c: single start position
        width, height: dimensions of the ray
        dr, dc: direction
        is_horizontal: True if moving horizontally, False if vertically
        bounce_depth: current bounce depth (0 for initial rays, max 2)
        parent_direction: 'left', 'right', 'up', 'down' to track ray origin
        """
        # Limit to 2 bounces maximum (depth 0 = initial ray, depth 1-2 = bounces)
        if bounce_depth > 2:
            return
        
        cells = []
        hit_info = None
        
        # Generate positions based on direction
        if is_horizontal:
            # Moving horizontally, width in vertical direction
            current_positions = [(start_r + h, start_c ) for h in range(height)]
        else:
            # Moving vertically, width in horizontal direction
            current_positions = [(start_r, start_c + w ) for w in range(width)]
        # Shoot in the given direction
        while True:
            # Move all positions in direction
            current_positions = [(r + dr, c + dc) for r, c in current_positions]
            
            # Check if any position is out of bounds
            if any(r < 0 or r >= grid.height or c < 0 or c >= grid.width for r, c in current_positions):
                break
            
            # Check if hit a colored block
            for r, c in current_positions:
                cell_val = grid[r][c]
                if cell_val in segment_info:
                    hit_info = cell_val
                    break
            
            if hit_info:
                break
            
            # Check if all positions can pass
            can_pass_all = True
            for r, c in current_positions:
                can_pass = is_empty(r, c) or (bounce_depth > 0 and grid[r][c] == 8)
                if not can_pass:
                    can_pass_all = False
                    break
            
            if can_pass_all:
                # Only add to cells list if it's empty background (not already 8)
                for r, c in current_positions:
                    if is_empty(r, c):
                        cells.append((r, c))
            else:
                break
        
        # Draw the line FIRST before creating bounces
        draw_line(cells)
        
        # If hit a block, create perpendicular bounce
        if hit_info:
            color = hit_info
            
            
            # Find the "first" position in the current ray to use as bounce reference
            # Get the last valid positions before the hit
            last_positions = [(r - dr, c - dc) for r, c in current_positions]
            if is_horizontal:
                # For horizontal ray, get topmost position (min row)
                ref_r = min(r for r, c in last_positions)
                ref_c = last_positions[0][1]
            else:
                # For vertical ray, get leftmost position (min col)
                ref_r = last_positions[0][0]
                ref_c = min(c for r, c in last_positions)
            
            if is_horizontal:
                # Horizontal ray → Vertical bounce (perpendicular)
                # Bounce is now vertical, starts from ref position with swapped dimensions
                if parent_direction == 'right':
                    ref_c -= width - 1
                if (segment_info[color] == 'left' and parent_direction == 'right') or (segment_info[color] == 'right' and parent_direction == 'left'):
                    shoot_and_bounce(ref_r, ref_c, height, width, -1, 0, False, bounce_depth + 1, 'up')
                else:
                    shoot_and_bounce(ref_r, ref_c, height, width, 1, 0, False, bounce_depth + 1, 'down')
            
            else:
                # Vertical ray → Horizontal bounce (perpendicular)
                # Bounce is now horizontal, starts from ref position with swapped dimensions
                if parent_direction == 'down':
                    ref_r -= height - 1
                if (segment_info[color] == 'left' and parent_direction == 'down') or (segment_info[color] == 'right' and parent_direction == 'up'):
                    # At left side → bounce LEFT (towards left edge/outer)
                    shoot_and_bounce(ref_r, ref_c, width, height, 0, 1, True, bounce_depth + 1, 'right')
                else:
                    # At right side → bounce RIGHT (towards right edge/outer)
                    shoot_and_bounce(ref_r, ref_c, width, height, 0, -1, True, bounce_depth + 1, 'left')
                    
    
    # Shoot 4 main rays from center
    # # UP
    shoot_and_bounce(center_r, center_c, gun_width, gun_height, -1, 0, False, 0, 'up')
    
    # # DOWN  
    shoot_and_bounce(center_r + gun_height - 1, center_c, gun_width, gun_height, 1, 0, False, 0, 'down')
    
    # # RIGHT
    shoot_and_bounce(center_r, center_c + gun_width - 1, gun_width, gun_height, 0, 1, True, 0, 'right')
    
    # # LEFT
    shoot_and_bounce(center_r, center_c, gun_width, gun_height, 0, -1, True, 0, 'left')

    return grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py e87109e9 bouncer") 
