import os
from collections import Counter
from arc_tools.grid import Color, Grid, SubGrid, detect_objects, GridRegion, GridPoint, place_object_on_new_grid
from arc_tools import logger
from arc_tools.plot import plot_grids

def canals(grid: Grid):
    '''
    Creates red canals by:
    1. Main vertical canal at yellow marker
    2. go up til find a blue object
    3. extend canal in the green dots direction
    '''
    objects = detect_objects(grid)
    blue_objects = []
    for obj in objects:
        if obj.width == 1:
            main_canal = obj
        else:
            blue_objects.append(obj)

    processed_blue_objects = []
    def extend_canal(start_x, start_y, side):
        nonlocal processed_blue_objects
        if side == "top":
            is_yellow_marker = grid[start_y][start_x] == Color.YELLOW.value
            if is_yellow_marker:
                x_range = range(start_x, start_x + 1)
            else:
                x_range = range(start_x, start_x + 2)
            y_range = range(start_y+1, -1, -1)
        elif side == "bottom":
            x_range = range(start_x, start_x + 2)
            y_range = range(start_y, grid.height)
        elif side == "left":
            x_range = range(start_x + 1, -1, -1)
            y_range = range(start_y, start_y + 2)
        elif side == "right":
            x_range = range(start_x, grid.width)
            y_range = range(start_y, start_y + 2)
        
        if side in ["top", "bottom"]:
            for x in x_range:
                for y in y_range:
                    if grid[y][x] == Color.BLUE.value:
                        break
                    grid[y][x] = Color.RED.value
        elif side in ["left", "right"]:
            for y in y_range:
                for x in x_range:
                    if grid[y][x] == Color.BLUE.value:
                        break
                    grid[y][x] = Color.RED.value
        
        next_point = GridPoint(x, y)
        # find which obj contains next_point
        for obj in blue_objects:
            if obj.contains(next_point):
                next_obj = obj
                next_obj.replace_color(Color.BLUE, Color.RED)
                # check which side has green dot
                # top side
                green_value = Color.GREEN.value
                
                if any(top_side_check := [x == green_value for x in next_obj.get_top_side()]):
                    extend_canal(next_obj.region.x1 + top_side_check.index(True), next_obj.region.y1, "top")
                elif any(bottom_side_check := [x == green_value for x in next_obj.get_bottom_side()]):
                    extend_canal(next_obj.region.x1 + bottom_side_check.index(True), next_obj.region.y2, "bottom")
                elif any(left_side_check := [x == green_value for x in next_obj.get_left_side()]):
                    extend_canal(next_obj.region.x1, next_obj.region.y1 + left_side_check.index(True), "left")
                elif any(right_side_check := [x == green_value for x in next_obj.get_right_side()]):
                    extend_canal(next_obj.region.x2, next_obj.region.y1 + right_side_check.index(True), "right")
                processed_blue_objects.append(next_obj)
                break
    
    extend_canal(main_canal.region.x1, main_canal.region.y1, "top")
    for obj in blue_objects:
        if obj not in processed_blue_objects:
            grid.remove_object(obj)
    
    return grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 5961cc34 canals") 
