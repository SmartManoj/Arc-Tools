import os
from arc_tools import logger
from arc_tools.constants import EIGHT_DIRECTIONS
from arc_tools.grid import Grid, GridPoint

# logger.setLevel(10)

def connect_the_dots(grid: Grid):
    """
    Connect the dots in the grid in clockwise order.
    if a single dot is attached to another dot, then attach it to the other dots of the same color if it is background color.
    """
    
    result_grid = grid.copy()
    
    # Get all unique colors in the grid except the background color
    colors = [c for c in grid.get_unique_values() if c != grid.background_color]
    
    single_dots = []
    # Process each color
    for color in colors:
        # Find all dots of the current color
        dots = []
        for y in range(grid.height):
            for x in range(grid.width):
                if grid[y][x] == color:
                    dots.append(GridPoint(x, y))
        
        if len(dots) == 1:
            single_dots.append(dots[0])
            continue
        
        # If there are at least 2 dots of this color, connect them
        if len(dots) >= 2:
            # Sort dots in circular order (clockwise from top-left)
            # Calculate center point
            center_x = sum(dot.x for dot in dots) / len(dots)
            center_y = sum(dot.y for dot in dots) / len(dots)
            
            # Sort by angle from center (clockwise)
            import math
            def angle_from_center(dot):
                return math.atan2(dot.y - center_y, dot.x - center_x)
            
            dots.sort(key=angle_from_center)
            
            # Connect dots in a cycle: 1->2, 2->3, 3->1, etc.
            # But only if they are aligned (horizontal, vertical, or diagonal)
            for i in range(len(dots)):
                dot1 = dots[i]
                dot2 = dots[(i + 1) % len(dots)]  # Next dot, wrapping around to first
                
                # Calculate the offset
                dx = dot2.x - dot1.x
                dy = dot2.y - dot1.y
                
                # Only connect if dots are aligned (horizontal, vertical, or diagonal)
                if dx == 0 or dy == 0 or abs(dx) == abs(dy):
                    # Connect these dots with a line
                    steps = max(abs(dx), abs(dy))
                    
                    # Calculate step size for x and y
                    step_x = dx / steps if steps > 0 else 0
                    step_y = dy / steps if steps > 0 else 0
                    
                    # Draw the line
                    for step in range(steps + 1):
                        x = int(dot1.x + step * step_x)
                        y = int(dot1.y + step * step_y)
                        # Make sure we're not drawing outside the grid
                        if 0 <= x < grid.width and 0 <= y < grid.height:
                            result_grid[y][x] = color
    
    for single_dot in single_dots:
        # check it's nearby dot
        for direction in EIGHT_DIRECTIONS:
            x = single_dot.x + direction[0]
            y = single_dot.y + direction[1]
            if 0 <= x < grid.width and 0 <= y < grid.height:
                if grid[y][x] != grid.background_color:
                    required_color = grid[y][x]
                    required_direction = direction
                    break
        else:
            logger.info(f"No nearby dot found for {single_dot.x}, {single_dot.y}")
            continue
        # apply color to all dots of required_color in opposite direction if it is background color
        color = result_grid[single_dot.y][single_dot.x]
        for y in range(grid.height):
            for x in range(grid.width):
                if result_grid[y][x] == required_color:
                    new_x = x - required_direction[0]
                    new_y = y - required_direction[1]
                    if 0 <= new_x < grid.width and 0 <= new_y < grid.height:
                        if result_grid[new_y][new_x] == grid.background_color:
                            result_grid[new_y][new_x] = color
    
    return result_grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 35ab12c3 connect_the_dots")
    