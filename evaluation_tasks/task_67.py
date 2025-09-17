import os
from arc_tools.grid import Grid, detect_objects, move_object, place_object
from arc_tools import logger
from arc_tools.plot import plot_grids

def get_direction_from_hint_box(hint_box):
        """Determine direction based on red position in hint_box"""
        # Use only red position to determine direction since blue may be background
        grid_data = hint_box
        
        # Find red (2) position
        red_positions = []
        
        for y in range(grid_data.height):
            for x in range(grid_data.width):
                if grid_data[y][x] == 2:  # Red
                    red_positions.append((x, y))
        
        red_x, red_y = red_positions[0]
        red_x2, red_y2 = red_positions[1]
        
        center_x = grid_data.width // 2
        center_y = grid_data.height // 2
        dx = red_x - center_x
        dy = red_y - center_y
        if red_x == red_x2:
            return 'right' if dx > 0 else 'left'
        elif red_y == red_y2:
            return 'down' if dy > 0 else 'up'
        else:  # Diagonal movement
            if dy >= 0:
                if dx >= 0:
                    return 'bottom-right'
                else:
                    return 'bottom-left'
            else:
                if dx < 0:
                    return 'top-right'
                else:
                    return 'top-left'
    

def shooting_stars(grid: Grid):
    '''
    Move yellow stars (4) based on directional indicators in their frames.
    Stars move in the direction indicated by red-pointed arrow directions.
    '''
    result = grid.copy()
    objects = detect_objects(grid, single_color_only=0)
    hint_boxes = []
    stars = []
    frames = []
    for obj in objects:
        if obj.get_holes_count() == 0 and obj.area != 1:
            hint_boxes.append(obj)
            grid.remove_object(obj)
    
    objects = detect_objects(grid, single_color_only=1)
    for obj in objects:
        if obj.area == 1:
            stars.append(obj)
        else:
            frames.append(obj)

    
    hint_directions = {hint_box[0][0]: get_direction_from_hint_box(hint_box) for hint_box in hint_boxes}
    for star in stars:
        for frame in frames:
            if frame.region.contains(star.region):
                hint_direction = hint_directions[frame.color]
                
                if hint_direction == 'right':
                    for x in range(star.region.x1, grid.width-1):
                        if grid[star.region.y1][x+1] == frame.color:
                            place_object(star, x, star.region.y1, result)
                            break
                elif hint_direction == 'left':
                    for x in range(star.region.x1, 0, -1):
                        if grid[star.region.y1][x-1] == frame.color:
                            place_object(star, x, star.region.y1, result)
                            break
                elif hint_direction == 'bottom-right':
                    # Move diagonally bottom-right until hitting the frame color
                    x, y = star.region.x1, star.region.y1
                    while x < grid.width-1 and y < grid.height-1:
                        x += 1
                        y += 1
                        if grid[y + 1][x + 1] == frame.color:
                            place_object(star, x, y, result)
                            break
                elif hint_direction == 'down':
                    for y in range(star.region.y1, grid.height-1):
                        if grid[y+1][star.region.x1] == frame.color:
                            place_object(star, star.region.x1, y, result)
                            break
                elif hint_direction == 'up':
                    for y in range(star.region.y1, 0, -1):
                        if grid[y-1][star.region.x1] == frame.color:
                            place_object(star, star.region.x1, y, result)
                            break
                elif hint_direction == 'top-right':
                    x, y = star.region.x1, star.region.y1
                    while x < grid.width-1 and y > 0:
                        x += 1
                        y -= 1
                        if grid[y][x] == frame.color:
                            place_object(star, x, y, result)
                            break
                elif hint_direction == 'bottom-left':
                    x, y = star.region.x1, star.region.y1
                    while x > 0 and y < grid.height-1:
                        x -= 1
                        y += 1
                        if grid[y + 1][x + 1] == frame.color:
                            place_object(star, x, y, result)
                            break
                elif hint_direction == 'top-left':
                    x, y = star.region.x1, star.region.y1
                    while x > 0 and y > 0:
                        x -= 1
                        y -= 1
                        if grid[y - 1][x - 1] == frame.color:
                            place_object(star, x, y, result)
                            break
                break
    return result

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 88e364bc shooting_stars") 
