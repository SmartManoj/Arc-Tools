import os
from arc_tools.grid import Color, Grid, detect_objects, move_object

# logger.setLevel(10)

def travel(grid: Grid):
    """
    Black box moves in a snake-like pattern: left, down, right, up, repeat.
    """
    rows, cols = len(grid), len(grid[0])
    
    # Detect black box
    black_boxes = detect_objects(grid, required_color=Color.BLACK, single_color_only=True)
    black_box = black_boxes[0]
    
    # Set up movement parameters
    steps_taken = 0
    
    # Start with right movement, but avoid undoing previous steps
    directions = ["right", "down", "left", "up"]
    direction_index = 0
    current_direction = directions[direction_index]
    previous_direction = None
    
    # Helper function to check if we can move in a given direction
    def can_move_in_direction(direction):
        required_colors = [Color.BLUE.value, Color.RED.value]
        if direction == "left":
            x = black_box.region.x1 - 1
            if x >= 0:
                for y in range(black_box.region.y1, black_box.region.y2 + 1):
                    if grid[y][x] not in required_colors:
                        return False
                return True
            return False
        elif direction == "right":
            x = black_box.region.x2 + 1
            if x < cols:
                for y in range(black_box.region.y1, black_box.region.y2 + 1):
                    if grid[y][x] not in required_colors:
                        return False
                return True
            return False
        elif direction == "up":
            y = black_box.region.y1 - 1
            if y >= 0:
                for x in range(black_box.region.x1, black_box.region.x2 + 1):
                    if grid[y][x] not in required_colors:
                        return False
                return True
            return False
        elif direction == "down":
            y = black_box.region.y2 + 1
            if y < rows:
                for x in range(black_box.region.x1, black_box.region.x2 + 1):
                    if grid[y][x] not in required_colors:
                        return False
                return True
        return False
    
    # Helper function to move in a given direction
    def move_in_direction(direction):
        if direction == "left":
            return move_object(black_box, -1, 0, grid, fill_color=Color.BLUE)
        elif direction == "right":
            return move_object(black_box, 1, 0, grid, fill_color=Color.BLUE)
        elif direction == "up":
            return move_object(black_box, 0, -1, grid, fill_color=Color.BLUE)
        elif direction == "down":
            return move_object(black_box, 0, 1, grid, fill_color=Color.BLUE)
        return black_box
    
    # Main loop
    while 1:
        
        # Check if the current direction would undo the previous step
        opposite_directions = {"right": "left", "left": "right", "up": "down", "down": "up"}
        if previous_direction and current_direction == opposite_directions.get(previous_direction):
            # Skip this direction and try the next one
            direction_index = (direction_index + 1) % len(directions)
            current_direction = directions[direction_index]
            continue
        
        # Check if we can move in the current direction
        if can_move_in_direction(current_direction):
            # Move in the current direction
            black_box = move_in_direction(current_direction)
            previous_direction = current_direction  # Remember this direction
            steps_taken += 1
        else:
            # Try the next direction in the pattern
            direction_index = (direction_index + 1) % len(directions)
            current_direction = directions[direction_index]
            
            # If we've tried all directions and can't move, stop
            directions_to_try = [d for d in directions if d != opposite_directions.get(previous_direction, None)]
            if not any(can_move_in_direction(d) for d in directions_to_try):
                break
    
    # Final visualization
    return grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 332f06d7 travel")
