import os
from arc_tools.grid import Grid, detect_objects

# logger.setLevel(10)

def extend_the_nose(grid: Grid):
    """
    For each multi-colored object, find the minority color dots and extend them
    in a line away from the nose (single dot on the border but not on the corner).
    conditions: there should be at least 1 space from the edge of the nose of the majority object.
    """
    result = grid.copy()
    
    # Detect all objects in the grid
    objects = detect_objects(grid)
    
    # Process each object to find multi-colored ones
    for obj in objects:
            
        color_positions = {}
        
        for y in range(obj.height):
            for x in range(obj.width):
                cell_value = obj.get(x, y)
                if cell_value != obj.background_color:
                    if cell_value not in color_positions:
                        color_positions[cell_value] = []
                    parent_x = obj.region.x1 + x
                    parent_y = obj.region.y1 + y
                    color_positions[cell_value].append((parent_x, parent_y))
        
        if len(color_positions) == 1:
            continue
            
        # Find the majority color (main object) and minority colors (dots to extend)
        color_counts = {color: len(positions) for color, positions in color_positions.items()}
        majority_color = max(color_counts, key=color_counts.get)
        minority_color = min(color_counts, key=color_counts.get)
        if 1:
            # This is a minority color - extend it
            minority_positions = color_positions[minority_color]
            majority_positions = color_positions[majority_color]
            
            # Remove original minority color positions
            for pos_x, pos_y in minority_positions:
                result.set(pos_x, pos_y, obj.background_color)
            
            # Find the bounds of the majority color
            majority_min_x = min(pos[0] for pos in majority_positions)
            majority_max_x = max(pos[0] for pos in majority_positions)
            majority_min_y = min(pos[1] for pos in majority_positions)
            majority_max_y = max(pos[1] for pos in majority_positions)
            
            # Find which border of the majority object has single/isolated dots
            # Check each border for density of majority color dots
            
            # Count majority dots on each border
            top_border_dots = sum(1 for pos_x, pos_y in majority_positions if pos_y == majority_min_y)
            bottom_border_dots = sum(1 for pos_x, pos_y in majority_positions if pos_y == majority_max_y)
            left_border_dots = sum(1 for pos_x, pos_y in majority_positions if pos_x == majority_min_x)
            right_border_dots = sum(1 for pos_x, pos_y in majority_positions if pos_x == majority_max_x)
            
            
            # Find the border with the fewest majority dots (most sparse)
            valid_borders = [
                (top_border_dots, 'top'),
                (bottom_border_dots, 'bottom'),
                (left_border_dots, 'left'),
                (right_border_dots, 'right')
            ]
            
            
            # Find the border with minimum density (most sparse)
            min_density = min(valid_borders, key=lambda x: x[0])[0]
            sparse_borders = [border for density, border in valid_borders if density == min_density]
            
            # If there are multiple sparse borders, avoid corners/edges and prioritize safe directions
            best_border = None
            
            # Check each sparse border to see if it would place nose on corner/edge
            for border in sparse_borders:
                if border == 'top':
                    # Check if extending UP would place nose too close to top edge
                    is_corner_emtpty = all(result.get(x,majority_min_y) == grid.background_color for x in (majority_min_x,majority_max_x))
                    if majority_min_y >= 1 and is_corner_emtpty:  # At least 1 space from edge
                        best_border = border
                elif border == 'bottom':
                    is_corner_emtpty = all(result.get(x,majority_max_y) == grid.background_color for x in (majority_min_x,majority_max_x))
                    if majority_max_y  < grid.height - 1 and is_corner_emtpty:  # At least 1 space from edge
                        best_border = border
                elif border == 'left':
                    # Check if extending LEFT would place nose too close to left edge
                    is_corner_emtpty = all(result.get(majority_min_x,y) == grid.background_color for y in (majority_min_y,majority_max_y))
                    if majority_min_x >= 1 and is_corner_emtpty:  # At least 1 space from edge
                        best_border = border
                elif border == 'right':
                    # Check if extending RIGHT has at least one valid position
                    is_corner_emtpty = all(result.get(majority_max_x,y) == grid.background_color for y in (majority_min_y,majority_max_y))
                    if majority_max_x < grid.width - 1 and is_corner_emtpty:  # At least first position is valid
                        best_border = border

            # Extend in the direction towards the sparse border (where single dots are)
            if best_border == 'top':
                # Sparse dots on top, extend UP
                direction = (0, -1)
                # Find minority dots closest to the top border, then pick the center one
                min_y = min(pos[1] for pos in minority_positions)
                top_dots = [pos for pos in minority_positions if pos[1] == min_y]
                # Use the median x-coordinate among the top dots
                top_dots.sort(key=lambda pos: pos[0])
                start_x = top_dots[len(top_dots) // 2][0]
                start_y = majority_min_y - 1
            elif best_border == 'bottom':
                # Sparse dots on bottom, extend DOWN
                direction = (0, 1)
                # Find minority dots closest to the bottom border, then pick the center one
                max_y = max(pos[1] for pos in minority_positions)
                bottom_dots = [pos for pos in minority_positions if pos[1] == max_y]
                # Use the median x-coordinate among the bottom dots
                bottom_dots.sort(key=lambda pos: pos[0])
                start_x = bottom_dots[len(bottom_dots) // 2][0]
                start_y = majority_max_y + 1
            elif best_border == 'left':
                # Sparse dots on left, extend LEFT
                direction = (-1, 0)
                target_y = None
                for pos_x, pos_y in majority_positions:
                    if pos_x == majority_min_x:
                        target_y = pos_y
                        break
                start_x = majority_min_x - 1
                start_y = target_y
            else:  # best_border == 'right'
                # Sparse dots on right, extend RIGHT
                direction = (1, 0)
                target_y = None
                for pos_x, pos_y in majority_positions:
                    if pos_x == majority_max_x:
                        target_y = pos_y
                        break
                start_x = majority_max_x + 1
                start_y = target_y
            
            # Extend the line
            current_x, current_y = start_x, start_y
            extension_length = len(minority_positions)  # Extend same number of cells as removed
            
            for _ in range(extension_length):
                if (0 <= current_x < grid.width and
                    0 <= current_y < grid.height and
                    result.get(current_x, current_y) == grid.background_color):
                    result.set(current_x, current_y, minority_color)
                    current_x += direction[0]
                    current_y += direction[1]
                else:
                    break
    
    return result

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 3dc255db extend_the_nose")
    
