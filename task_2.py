from collections import Counter
from arc_tools import grid
from arc_tools.grid import Grid, detect_objects, Color, SubGrid, GridRegion, GridPoint
from arc_tools.plot import plot_grid, plot_grids
from itertools import combinations
from arc_tools.logger import logger
from copy import deepcopy



def connect_center(grid: Grid) -> Grid:
    '''
    second last row - knowledge row - specifies the order of the connections
    square boxes - connect the center of the square boxes consecutively
    '''
    # Get the sequence from the knowledge row (second last row)
    knowledge_row = grid[-2]
    sequence = []
    for i in range(len(knowledge_row)):
        if knowledge_row[i] != grid.background_color:
            sequence.append(knowledge_row[i])

    objects = detect_objects(grid)
    # filter 1*1
    objects = [obj for obj in objects if obj.region.width > 1 or obj.region.height > 1]
    for obj in objects:
        obj.set_center_color()
    
    # Connect objects based on the sequence
    last_obj = None
    processed_objects = []
    for i in range(len(sequence) - 1):
        # Find objects with matching colors
        try:
            if last_obj is None:
                obj1 = next((obj for obj in objects if obj.center_color == sequence[i] and obj not in processed_objects), None)
                if obj1 is None:
                    logger.warning(f"No object found with color {Color(sequence[i]).name}")
                    continue
                processed_objects.append(obj1)
            else:
                obj1 = last_obj
            
            obj2 = next((obj for obj in objects if obj.center_color == sequence[i+1] and obj not in processed_objects), None)
            if obj2 is None:
                logger.warning(f"No object found with color {Color(sequence[i+1]).name}")
                continue
            processed_objects.append(obj2)
            last_obj = obj2
            
            
            if obj1 and obj2:
                # Calculate center points of both objects
                center1_x = (obj1.region.x1 + obj1.region.x2) // 2
                center1_y = (obj1.region.y1 + obj1.region.y2) // 2
                center2_x = (obj2.region.x1 + obj2.region.x2) // 2
                center2_y = (obj2.region.y1 + obj2.region.y2) // 2
                
                # Calculate the number of lines to draw based on the square root of the center color count
                num_lines = int(obj1.get_values_count()[obj1.center_color] ** 0.5)
                # Check if we need to draw horizontal line (objects on same y-level)
                if obj1.region.y1 == obj2.region.y1 and obj1.region.y2 == obj2.region.y2:
                    # Draw horizontal line
                    dx = 1 if center2_x > center1_x else -1 if center2_x < center1_x else 0
                    x_steps = abs(center2_x - center1_x)
                    
                    
                    for line_offset in range(num_lines):
                        current_x, current_y = center1_x, center1_y + line_offset
                        for step in range(x_steps + 1):
                            current_x = center1_x + (dx * step)
                            if (0 <= current_y < grid.height and 0 <= current_x < grid.width and 
                                grid[current_y][current_x] == grid.background_color):
                                grid[current_y][current_x] = obj1.center_color
                else:
                    # Draw vertical line for other connections
                    dy = 1 if center2_y > center1_y else -1 if center2_y < center1_y else 0
                    y_steps = abs(center2_y - center1_y)
                    
                    for line_offset in range(num_lines):
                        current_x, current_y = center1_x + line_offset, center1_y
                        for step in range(y_steps + 1):
                            current_y = center1_y + (dy * step)
                                
                            if (0 <= current_y < grid.height and 0 <= current_x < grid.width and 
                                grid[current_y][current_x] == grid.background_color):
                                grid[current_y][current_x] = obj1.center_color
                    
        except Exception as e:
            logger.error(f"Error processing connection {i}: {str(e)}")
            continue
    
    # plot_grid(grid, "connected_center.png", show=True)
    return grid

if __name__ == "__main__":
    import os
    os.system("main.py 3e6067c3 connect_center")