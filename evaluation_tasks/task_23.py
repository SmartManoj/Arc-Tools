import os
from arc_tools.grid import Grid, detect_objects, GridRegion, GridPoint
# logger.setLevel(10)


def remove_consecutive_duplicates(data):
    if not data:
        return []
    output = [data[0]]
    for i in range(1,len(data)):
        if data[i] != data[i-1]:
            output.append(data[i])
    return output

def draw_border(data_dict, key_dot_position, grid, primary_color, total_frames):
    left_distance = data_dict['left']
    right_distance = data_dict['right']
    top_distance = data_dict['top']
    bottom_distance = data_dict['bottom']
    length = max(left_distance, right_distance, top_distance, bottom_distance, total_frames*2+1)
    w = 0
    h = 0
    w1 = 0
    h1 = 0
    for i in range(2, length, 2):
        w += 2
        h += 2
        w1 += 2
        h1 += 2
        # logger.info(f"w: {w}, h: {h}, horizontal_position: {horizontal_position}, vertical_position: {vertical_position}")
        if grid[key_dot_position[1]][key_dot_position[0]- w] == primary_color:
            w += 2
        if grid[key_dot_position[1]][key_dot_position[0]+w1] == primary_color:
            w1 += 2
        if grid[key_dot_position[1]-h][key_dot_position[0]] == primary_color:
            h += 2
        if grid[key_dot_position[1]+h1][key_dot_position[0]] == primary_color:
            h1 += 2
        # top border
        for j in range(key_dot_position[0]-w, key_dot_position[0]+w1+1):
            grid[key_dot_position[1]-h][j] = primary_color
        # bottom border
        for j in range(key_dot_position[0]-w, key_dot_position[0]+w1+1):
            grid[key_dot_position[1]+h1][j] = primary_color
        # left border
        for j in range(key_dot_position[1]-h, key_dot_position[1]+h1+1):
            grid[j][key_dot_position[0]-w] = primary_color
        # right border
        for j in range(key_dot_position[1]-h, key_dot_position[1]+h1+1):
            grid[j][key_dot_position[0]+w1] = primary_color
    x1 = key_dot_position[0] - max(w, left_distance-1)
    y1 = key_dot_position[1] - max(h, top_distance-1)
    x2 = key_dot_position[0] + max(w1, right_distance+1)
    y2 = key_dot_position[1] + max(h1, bottom_distance+1)
    return GridRegion([GridPoint(x1, y1), GridPoint(x2, y2)])

def squeeze(grid: Grid):
    """ 
    change inner objects to single dots.
    stright the border.
    """
    # Detect all objects in the grid
    objects = detect_objects(grid)
    # Process each object
    first_obj_x = None
    first_obj_y = None
    new_dot_positions = []
    primary_color = grid.get_max_color()
    for obj in objects:
        # Check if object has no holes
        if not obj.has_hollow_space():
            # Get object color
            grid.remove_object(obj)
            
            # Place a single dot at the center of where the object was
            last_dot_x = obj.region.x2
            last_dot_y = obj.region.y2
            if first_obj_x is None:
                first_obj_x = last_dot_x
                first_obj_y = last_dot_y
            else:
                # logger.info(f"center_x: {center_x}, first_obj_x: {first_obj_x}")
                if last_dot_x != first_obj_x and obj.region.x1 <= first_obj_x <= obj.region.x2:
                    last_dot_x = first_obj_x
                if last_dot_y != first_obj_y and obj.region.y1 <= first_obj_y <= obj.region.y2:
                    last_dot_y = first_obj_y
            new_dot_positions.append((last_dot_x, last_dot_y))
            grid[last_dot_y][last_dot_x] = primary_color
    total_frames = len(objects) - len(new_dot_positions)
    result = grid.get_frame()
    # find the key dot position that has dots on horizontal and vertical 
    for i,dot_position in enumerate(new_dot_positions):
        remaining_dot_positions = [dot_position1 for j,dot_position1 in enumerate(new_dot_positions) if j != i]
        if any(dot_position[0] == dot_position1[0] for dot_position1 in remaining_dot_positions) and any(dot_position[1] == dot_position1[1] for dot_position1 in remaining_dot_positions):
            key_dot_position = dot_position
            break
    else:
        new_dot_positions.sort(key=lambda x: x[0])
        key_dot_position = new_dot_positions[0]
        remaining_dot_positions = new_dot_positions[1:] if len(new_dot_positions) > 1 else []
    # place first dot
    result[key_dot_position[1]][key_dot_position[0]] = primary_color
    data_dict = {'left':0, 'right':0, 'top':0, 'bottom':0}
    for dot_position in remaining_dot_positions:
        if dot_position[1] == key_dot_position[1]:
            # horizontal
            if dot_position[0] >= key_dot_position[0]:
                data = grid[dot_position[1]][key_dot_position[0]:dot_position[0]+1]
            else:
                data = grid[dot_position[1]][dot_position[0]:key_dot_position[0]+1]
            data = remove_consecutive_duplicates(data)
            # place the dots
            if dot_position[0] >= key_dot_position[0]:
                result[dot_position[1]][key_dot_position[0]+len(data)-1] = primary_color
                data_dict['right'] = len(data) - 1
            else:
                result[dot_position[1]][key_dot_position[0]-(len(data)-1)] = primary_color
                data_dict['left'] = len(data) - 1
        else:
            # vertical
            if dot_position[1] >= key_dot_position[1]:
                data = [grid[i][dot_position[0]] for i in range(key_dot_position[1],dot_position[1]+1)]
            else:
                data = [grid[i][dot_position[0]] for i in range(dot_position[1],key_dot_position[1]+1)]
            data = remove_consecutive_duplicates(data)
            # place the dots
            if dot_position[1] >= key_dot_position[1]:
                result[key_dot_position[1]+len(data)-1][dot_position[0]] = primary_color
                data_dict['bottom'] = len(data) - 1
            else:
                result[key_dot_position[1]-(len(data)-1)][dot_position[0]] = primary_color
                data_dict['top'] = len(data) - 1
    
    region = draw_border(data_dict, key_dot_position, result, primary_color, total_frames)
    result = result.crop(region)
    return result
    

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 2d0172a1 squeeze")