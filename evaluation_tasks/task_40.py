# optimize
import os
from collections import Counter
from arc_tools.grid import Color, Grid, SubGrid, detect_objects, GridRegion, GridPoint, place_object_on_new_grid, move_object, rotate_object, rotate_object_counter_clockwise
from arc_tools import logger
from arc_tools.plot import plot_grids

def race(grid: Grid):
    '''
    Moves the car to the road edge based on its direction.
    road edges are single dots.
    '''
    
    background_color = grid.background_color
    height, width = grid.height, grid.width
    
    # Initialize last_movement_direction
    last_movement_direction = None
    
    # Find vertical divider columns
    divider_cols = []
    for col in range(width):
        column_colors = [grid[row][col] for row in range(height)]
        unique_colors = set(column_colors)
        if len(unique_colors) == 1:
            color = list(unique_colors)[0]
            if color != background_color:
                divider_cols.append(col)
    
    if len(divider_cols) == 0:
        first_section = grid
    else:
        first_section_data = [row[:divider_cols[0]] for row in grid]
        first_section = Grid(first_section_data, background_color)
    car_objects = detect_objects(first_section)
    # ignore road edges
    car = [obj for obj in car_objects if obj.width * obj.height > 1][0]
    grid.remove_object(car)
    # Determine car direction
    if car.width < car.height:
        # car direction left or right
        # if single dot is first column, then car direction is left
        first_col = [i for i in range(1, car.height-1) if car[i][0] != grid.background_color]
        if len(first_col) == 1:
            car_direction = "left"
        else:
            car_direction = "right"
        
    elif car.width > car.height:
        # car direction up or down
        # if single dot is first row, then car direction is up
        first_row = [i for i in range(1, car.width-1) if car[0][i] != grid.background_color]
        if len(first_row) == 1:
            car_direction = "up"
            car_front_point = GridPoint(car.region.x1 + car.width // 2, car.region.y1)
        else:
            car_direction = "down"
            car_front_point = GridPoint(car.region.x1 + car.width // 2, car.region.y2)
    else:
        # found first row and column
        first_row = [i for i in range(1, car.width-1) if car[0][i] != grid.background_color]
        first_col = [i for i in range(1, car.height-1) if car[i][0] != grid.background_color]
        last_row = [i for i in range(1, car.width-1) if car[car.height - 1][i] != grid.background_color]
        last_col = [i for i in range(1, car.height-1) if car[i][car.width - 1] != grid.background_color]
        if len(first_row) == 1:
            car_direction = "up"
        elif len(last_row) == 1:
            car_direction = "down"
        elif len(first_col) == 1:
            car_direction = "left"
        elif len(last_col) == 1:
            car_direction = "right"
        else:
            return grid
    if car_direction == "left":
        car_front_point = GridPoint(car.region.x1, car.region.y1 + car.height // 2)
    elif car_direction == "right":
        car_front_point = GridPoint(car.region.x2, car.region.y1 + car.height // 2)
    elif car_direction == "up":
        car_front_point = GridPoint(car.region.x1 + car.width // 2, car.region.y1)
    elif car_direction == "down":
        car_front_point = GridPoint(car.region.x1 + car.width // 2, car.region.y2)
    
    # Create output grid with first section dimensions
    output_grid = Grid([[background_color for _ in range(first_section.width)] for _ in range(first_section.height)], background_color)
    
    # Calculate new position based on direction
    starting_car_front_point = car_front_point
    car_color = car.color
    
    if car_direction == "left":
        # Move car till a road edge is found
        new_col = starting_car_front_point.x
        new_row = starting_car_front_point.y
        # track new col
        while new_col > 1:
            new_col -= 1
            if grid[new_row][new_col] == car_color:
                break
        
        # After moving left, check up and down for road edges
        # Check up direction
        check_row_up = new_row
        while check_row_up > 0:
            check_row_up -= 1
            if grid[check_row_up][new_col] == car_color:
                new_row = check_row_up
                break
        
        # Check down direction
        check_row_down = new_row
        while check_row_down < first_section.height - 1:
            check_row_down += 1
            if grid[check_row_down][new_col] == car_color:
                new_row = check_row_down
                break
        
        
        # Check all three other directions repeatedly
        visited_positions = set()
        visited_positions.add((new_row, new_col))
        while True:
            moved = False
            
            # Check left direction
            check_col_left = new_col
            while check_col_left > 0:
                check_col_left -= 1
                if grid[new_row][check_col_left] == car_color:
                    if (new_row, check_col_left) not in visited_positions:
                        new_col = check_col_left
                        visited_positions.add((new_row, new_col))
                        moved = True
                        last_movement_direction = "left"
                        break
            
            if not moved:
                # Check right direction
                check_col_right = new_col
                while check_col_right < first_section.width - 1:
                    check_col_right += 1
                    if grid[new_row][check_col_right] == car_color:
                        if (new_row, check_col_right) not in visited_positions:
                            new_col = check_col_right
                            visited_positions.add((new_row, new_col))
                            moved = True
                            last_movement_direction = "right"
                            break
            
            if not moved:
                # Check up direction
                check_row_up = new_row
                while check_row_up > 0:
                    check_row_up -= 1
                    if grid[check_row_up][new_col] == car_color:
                        if (check_row_up, new_col) not in visited_positions:
                            new_row = check_row_up
                            visited_positions.add((new_row, new_col))
                            moved = True
                            last_movement_direction = "up"
                            break
            
            if not moved:
                # Check down direction
                check_row_down = new_row
                while check_row_down < first_section.height - 1:
                    check_row_down += 1
                    if grid[check_row_down][new_col] == car_color:
                        if (check_row_down, new_col) not in visited_positions:
                            new_row = check_row_down
                            visited_positions.add((new_row, new_col))
                            moved = True
                            last_movement_direction = "down"
                            break
            
            if not moved:
                break
    
    elif car_direction == "right":
        # Move car till a road edge is found
        new_col = starting_car_front_point.x
        new_row = starting_car_front_point.y
        while new_col < first_section.width - 2:
            new_col += 1
            if grid[new_row][new_col] == car_color:
                break
        
        # After moving right, check up and down for road edges
        # Check up direction
        check_row_up = new_row
        while check_row_up > 0:
            check_row_up -= 1
            if grid[check_row_up][new_col] == car_color:
                new_row = check_row_up
                break
        
        # Check down direction
        check_row_down = new_row
        while check_row_down < first_section.height - 1:
            check_row_down += 1
            if grid[check_row_down][new_col] == car_color:
                new_row = check_row_down
                break
        
        
        # Check all three other directions repeatedly
        visited_positions = set()
        visited_positions.add((new_row, new_col))
        while True:
            moved = False
            
            # Check left direction
            check_col_left = new_col
            while check_col_left > 0:
                check_col_left -= 1
                if grid[new_row][check_col_left] == car_color:
                    if (new_row, check_col_left) not in visited_positions:
                        new_col = check_col_left
                        visited_positions.add((new_row, new_col))
                        moved = True
                        last_movement_direction = "left"
                        break
            
            if not moved:
                # Check right direction
                check_col_right = new_col
                while check_col_right < first_section.width - 1:
                    check_col_right += 1
                    if grid[new_row][check_col_right] == car_color:
                        if (new_row, check_col_right) not in visited_positions:
                            new_col = check_col_right
                            visited_positions.add((new_row, new_col))
                            moved = True
                            last_movement_direction = "right"
                            break
            
            if not moved:
                # Check up direction
                check_row_up = new_row
                while check_row_up > 0:
                    check_row_up -= 1
                    if grid[check_row_up][new_col] == car_color:
                        if (check_row_up, new_col) not in visited_positions:
                            new_row = check_row_up
                            visited_positions.add((new_row, new_col))
                            moved = True
                            last_movement_direction = "up"
                            break
            
            if not moved:
                # Check down direction
                check_row_down = new_row
                while check_row_down < first_section.height - 1:
                    check_row_down += 1
                    if grid[check_row_down][new_col] == car_color:
                        if (check_row_down, new_col) not in visited_positions:
                            new_row = check_row_down
                            visited_positions.add((new_row, new_col))
                            moved = True
                            last_movement_direction = "down"
                            break
            
            if not moved:
                break
    
    elif car_direction == "up":
        # Move car till a road edge is found
        new_col = starting_car_front_point.x
        new_row = starting_car_front_point.y
        while new_row > 1:
            new_row -= 1
            if grid[new_row][new_col] == car_color:
                grid[new_row][new_col] = background_color
                break
        
        # After moving up, check left and right for road edges
        # Check left direction
        check_col_left = new_col
        while check_col_left > 0:
            check_col_left -= 1
            if grid[new_row][check_col_left] == car_color:
                new_col = check_col_left
                grid[new_row][new_col] = background_color
                break
        
        # Check right direction
        check_col_right = new_col
        while check_col_right < first_section.width - 1:
            check_col_right += 1
            if grid[new_row][check_col_right] == car_color:
                new_col = check_col_right
                grid[new_row][new_col] = background_color
                break
        
        
        # Check all three other directions repeatedly
        visited_positions = set()
        visited_positions.add((new_row, new_col))
        while True:
            moved = False
            
            # Check left direction
            check_col_left = new_col
            while check_col_left > 0:
                check_col_left -= 1
                if grid[new_row][check_col_left] == car_color:
                    if (new_row, check_col_left) not in visited_positions:
                        new_col = check_col_left
                        visited_positions.add((new_row, new_col))
                        moved = True
                        last_movement_direction = "left"
                        break
            
            if not moved:
                # Check right direction
                check_col_right = new_col
                while check_col_right < first_section.width - 1:
                    check_col_right += 1
                    if grid[new_row][check_col_right] == car_color:
                        if (new_row, check_col_right) not in visited_positions:
                            new_col = check_col_right
                            visited_positions.add((new_row, new_col))
                            moved = True
                            last_movement_direction = "right"
                            break
            
            if not moved:
                # Check up direction
                check_row_up = new_row
                while check_row_up > 0:
                    check_row_up -= 1
                    if grid[check_row_up][new_col] == car_color:
                        if (check_row_up, new_col) not in visited_positions:
                            new_row = check_row_up
                            visited_positions.add((new_row, new_col))
                            moved = True
                            last_movement_direction = "up"
                            break
            
            if not moved:
                # Check down direction
                check_row_down = new_row
                while check_row_down < first_section.height - 1:
                    check_row_down += 1
                    if grid[check_row_down][new_col] == car_color:
                        if (check_row_down, new_col) not in visited_positions:
                            new_row = check_row_down
                            visited_positions.add((new_row, new_col))
                            moved = True
                            last_movement_direction = "down"
                            break
            
            if not moved:
                break
    
    elif car_direction == "down":
        # Move car till a road edge is found
        new_col = starting_car_front_point.x
        new_row = starting_car_front_point.y
        while new_row < first_section.height - 2:
            new_row += 1
            if grid[new_row][new_col] == car_color:
                grid[new_row][new_col] = background_color
                break
        
        # After moving down, check left and right for road edges
        # Check left direction
        check_col_left = new_col
        while check_col_left > 0:
            check_col_left -= 1
            if grid[new_row][check_col_left] == car_color:
                new_col = check_col_left
                grid[new_row][new_col] = background_color
                break
        
        # Check right direction
        check_col_right = new_col
        while check_col_right < first_section.width - 1:
            check_col_right += 1
            if grid[new_row][check_col_right] == car_color:
                new_col = check_col_right
                grid[new_row][new_col] = background_color
                break
        
        
        # Check all three other directions repeatedly
        visited_positions = set()
        visited_positions.add((new_row, new_col))
        while True:
            moved = False
            
            # Check left direction
            check_col_left = new_col
            while check_col_left > 0:
                check_col_left -= 1
                if grid[new_row][check_col_left] == car_color:
                    if (new_row, check_col_left) not in visited_positions:
                        new_col = check_col_left
                        visited_positions.add((new_row, new_col))
                        moved = True
                        last_movement_direction = "left"
                        break
            
            if not moved:
                # Check right direction
                check_col_right = new_col
                while check_col_right < first_section.width - 1:
                    check_col_right += 1
                    if grid[new_row][check_col_right] == car_color:
                        if (new_row, check_col_right) not in visited_positions:
                            new_col = check_col_right
                            visited_positions.add((new_row, new_col))
                            moved = True
                            last_movement_direction = "right"
                            break
            
            if not moved:
                # Check up direction
                check_row_up = new_row
                while check_row_up > 0:
                    check_row_up -= 1
                    if grid[check_row_up][new_col] == car_color:
                        if (check_row_up, new_col) not in visited_positions:
                            new_row = check_row_up
                            visited_positions.add((new_row, new_col))
                            moved = True
                            last_movement_direction = "up"
                            break
            
            if not moved:
                # Check down direction
                check_row_down = new_row
                while check_row_down < first_section.height - 1:
                    check_row_down += 1
                    if grid[check_row_down][new_col] == car_color:
                        if (check_row_down, new_col) not in visited_positions:
                            new_row = check_row_down
                            visited_positions.add((new_row, new_col))
                            moved = True
                            last_movement_direction = "down"
                            break
            
            if not moved:
                break
    
    x1_cfp = starting_car_front_point.x - car.region.x1
    y1_cfp = starting_car_front_point.y - car.region.y1
    # Rotate car based on last movement direction
    # update the logic based on car direction
    directions = ['up', 'right', 'down', 'left'] 
    number_of_turns = (directions.index(last_movement_direction) - directions.index(car_direction)) % 4
    # x1_cfp, y1_cfp 

    # Store original car dimensions before rotation
    original_car_width = car.width
    original_car_height = car.height
    # plot_grids([car, output_grid])

    for _ in range(number_of_turns):
        car = rotate_object(car)
        
    
    # Adjust position coordinates based on number of rotations
    if number_of_turns % 4 == 1:  # 90 degrees clockwise
        # Transform coordinates for 90-degree rotation
        new_x1_cfp = -y1_cfp
        new_y1_cfp = -x1_cfp
        x1_cfp, y1_cfp = new_x1_cfp, new_y1_cfp
    elif number_of_turns % 4 == 2:  # 180 degrees
        # Transform coordinates for 180-degree rotation
        x1_cfp = -x1_cfp
        y1_cfp = y1_cfp - (original_car_height - 1 )
    elif number_of_turns % 4 == 3:  # 270 degrees clockwise (or 90 counter-clockwise)
        # Transform coordinates for 270-degree rotation
        new_x1_cfp = -y1_cfp
        new_y1_cfp = x1_cfp - (original_car_width - 1)
        x1_cfp, y1_cfp = new_x1_cfp, new_y1_cfp
    
    new_row = new_row + ( y1_cfp)
    new_col = new_col + ( x1_cfp)
    car = place_object_on_new_grid(car, new_col, new_row, output_grid)
    return output_grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 5545f144 race") 
