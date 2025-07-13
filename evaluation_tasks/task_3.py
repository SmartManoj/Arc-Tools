from arc_tools.grid import Grid, detect_objects, Color, place_object_on_new_grid, GridRegion, GridPoint, SubGrid

def is_pluggable(list_1, list_2):
    '''
    Check if list_1 and list_2 are pluggable by xor and sum is 1.
    '''
    return sum(a != b for a, b in zip(list_1, list_2)) == len(list_1) and list_1 and list_2

def is_pluggable_object(obj_1, obj_2, hole_side):
    '''
    Check if obj_2 can be placed on hole_side of obj_1.
    obj_1 is assumed to be an object already placed on a grid (e.g., the result grid).
    obj_2 is an object from the original set of flying objects.
    Their solidity is determined by their respective parent_grid.background_color.
    '''
    # Background color for obj_1 (e.g., from result grid)
    bg_color_obj_1 = obj_1.parent_grid.background_color 
    # Background color for obj_2 (e.g., from original input grid)
    bg_color_obj_2 = obj_2.parent_grid.background_color
    if hole_side in ['top', 'bottom']:
        if obj_1.width == obj_2.width:
            obj_1_top_row = [obj_1.get(x, 0) != bg_color_obj_1 for x in range(obj_1.width)]
            obj_2_bottom_row = [obj_2.get(x, obj_2.height - 1) != bg_color_obj_2 for x in range(obj_2.width)]
            
            if is_pluggable(obj_1_top_row, obj_2_bottom_row):
                return "top", 0
            
            for y in range(obj_1.height):
                obj_1_row = [obj_1.get(x, y) != bg_color_obj_1 for x in range(obj_1.width)]
                if sum(obj_1_row) == obj_1.width:
                    continue
                obj_2_top_row = [obj_2.get(x, 0) != bg_color_obj_2 for x in range(obj_2.width)]
                if is_pluggable(obj_1_row, obj_2_top_row):
                    return "bottom", 0
    else:
        if obj_1.height == obj_2.height:
            if hole_side == 'left':
                # iterate from the left and find the first non-background color
                obj_1_left_col = []
                previous_col = []
                for x in range(obj_1.width):
                    col = [obj_1.get(x, y) != bg_color_obj_1 for y in range(obj_1.height)]
                    if sum(col) == obj_1.height:
                        obj_1_left_col = (previous_col)
                        break
                    previous_col = col
                obj_2_right_col = [obj_2.get(obj_2.width - 1, y) != bg_color_obj_2 for y in range(obj_2.height)]
                if is_pluggable(obj_1_left_col, obj_2_right_col):
                    return "left",  x
            else:
                obj_1_right_col = []
                previous_col = []
                for x in reversed(range(obj_1.width)):
                    col = [obj_1.get(x, y) != bg_color_obj_1 for y in range(obj_1.height)]
                    if sum(col) == obj_1.height:
                        obj_1_right_col = (previous_col)
                        break
                    previous_col = col
                obj_2_left_col = [obj_2.get(0, y) != bg_color_obj_2 for y in range(obj_2.height)]
                if is_pluggable(obj_1_right_col, obj_2_left_col):
                    return "right", 0
    return None, 0

def is_pluggable_object_v2(obj_1, obj_2):
    for y in range(obj_1.height):
        for x in range(obj_1.width):
            obj_1_pixel = obj_1.get(x, y) != obj_1.background_color
            obj_2_pixel = obj_2.get(x, y) != obj_2.background_color
            if obj_1_pixel == obj_2_pixel:
                return False
    return True
    
def get_docker_inner_holes(docker_obj: Grid):
    '''
    Get the inner holes of the docker object.
    '''
    holes = []
    visited = set()
    for y in range(docker_obj.height):
        for x in range(docker_obj.width):
            if docker_obj.get(x, y) == docker_obj.background_color and (x, y) not in visited:
                current_hole = []
                q = [(x, y)]
                visited.add((x, y))
                while q:
                    px, py = q.pop(0)
                    current_hole.append(GridPoint(px + docker_obj.region.x1, py + docker_obj.region.y1))
                    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                        nx, ny = px + dx, py + dy
                        if 0 <= nx < docker_obj.width and 0 <= ny < docker_obj.height and \
                           docker_obj.get(nx, ny) == docker_obj.background_color and (nx, ny) not in visited:
                            visited.add((nx, ny))
                            q.append((nx, ny))
                holes.append(SubGrid(GridRegion(current_hole), docker_obj.parent_grid))
    return holes



def is_pluggable_object_to_hole(obj, hole, is_vertical_docker, hole_side):
    if is_vertical_docker:
        # Scan the whole width of the hole for pluggability from the left
        for y in range(obj.height - hole.height + 1):
            if hole_side == 'left':
                x1 = obj.region.x2 - hole.width + 1
            else:
                x1 = obj.region.x1
            x2 = x1 + hole.width - 1
            y1 = obj.region.y1 + y
            y2 = y1 + hole.height - 1
            sub_obj = SubGrid(GridRegion([GridPoint(x1, y1), GridPoint(x2, y2)]), obj.parent_grid)
            if is_pluggable_object_v2(sub_obj, hole):
                # ensure remaining region is empty
                y_index = y
                for x in range(x1, x2 + 1):
                    for y in range(obj.region.y1, obj.region.y2 + 1):
                        if y1 <= y <= y2:
                            continue
                        if obj.parent_grid.get(x, y) != obj.parent_grid.background_color:
                            return -1
                return y_index
    else:
        for x in range(obj.width - hole.width + 1):
            x1 = obj.region.x1 + x
            x2 = x1 + hole.width - 1
            if hole_side == 'top':
                y1 = obj.region.y2 - hole.height + 1
            else:
                y1 = obj.region.y1
            y2 = y1 + hole.height - 1
            sub_obj = SubGrid(GridRegion([GridPoint(x1, y1), GridPoint(x2, y2)]), obj.parent_grid)
            if is_pluggable_object_v2(sub_obj, hole):
                # ensure remaining region is empty
                # return x
                x_index = x
                for y in range(y1, y2 + 1):
                    for x in range(obj.region.x1, obj.region.x2 + 1):
                        if x1 <= x <= x2:
                            continue
                        if obj.parent_grid.get(x, y) != obj.parent_grid.background_color:
                            return -1
                return x_index
    return -1

def optimize_the_grid(grid: Grid) -> Grid:
    '''
    Optimize the grid by placing the flying objects on the docker object.
    '''
    result = Grid([[grid.background_color for _ in range(grid.width)] for _ in range(grid.height)], grid.background_color)
    
    docker_color_val = grid.get_max_color()
    flying_objects = detect_objects(grid, ignore_color=Color(docker_color_val))
    docker_obj = detect_objects(grid, required_color=Color(docker_color_val))[0]
    if docker_obj.height > docker_obj.width:
        is_vertical_docker = True
    else:
        is_vertical_docker = False
    
    place_object_on_new_grid(docker_obj, docker_obj.region.x1, docker_obj.region.y1, result)

    flying_objects.sort(key=lambda obj_item: (obj_item.region.y1, obj_item.region.x1))

    processed_other_indices = set()
    last_placed_main_stack_obj = None
    holes = get_docker_inner_holes(docker_obj)
    if is_vertical_docker:
        key_func = lambda x: (x.width, x.height)
    else:
        key_func = lambda x: (x.height, x.width)
    holes.sort(key=key_func, reverse=True)
    last_placed_main_stack_obj = None
    # 1. find first hole to place the main stack object
    for hole_idx, target_hole in enumerate(holes):
        if is_vertical_docker:
            hole_side = 'left' if target_hole.region.x1 == docker_obj.region.x1 else 'right'
            # check which obj can be placed on the target hole
            for obj_idx, obj in enumerate(flying_objects):
                if (y_index := is_pluggable_object_to_hole(obj, target_hole, is_vertical_docker, hole_side)) != -1:
                    last_placed_main_stack_obj = place_object_on_new_grid(obj, target_hole.region.x2 - obj.width + 1, target_hole.region.y1 - y_index, result)
                    last_hole_side = hole_side
                    processed_other_indices.add(obj_idx)
                    break
        else:
            # check which obj can be placed on the target hole
            hole_side = 'top' if target_hole.region.y1 == docker_obj.region.y1 else 'bottom'
            for obj_idx, obj in enumerate(flying_objects):
                if (index := is_pluggable_object_to_hole(obj, target_hole, is_vertical_docker, hole_side)) != -1:
                    new_x = target_hole.region.x1
                    new_y = target_hole.region.y1
                    if is_vertical_docker:
                        new_y -= index + 1
                    else:
                        new_x -= index
                        if hole_side == 'top':
                            new_y = target_hole.region.y2 - (obj.height - 1)
                    last_placed_main_stack_obj = place_object_on_new_grid(obj, new_x, new_y, result)
                    last_hole_side = hole_side
                    processed_other_indices.add(obj_idx)
                    break
        if last_placed_main_stack_obj:
            holes.pop(hole_idx)
            break
    # 2. Pluggable Stacking
    if last_placed_main_stack_obj:
        while True:
            plugged_in_this_iteration = False
            for i, other_obj in enumerate(flying_objects):
                if i in processed_other_indices:
                    continue
                
                side_to_plug, idx = is_pluggable_object(last_placed_main_stack_obj, other_obj, last_hole_side)
                if side_to_plug:
                    # Corrected
                    
                    plug_target_x, plug_target_y = -1, -1
                    if side_to_plug == "top":
                        plug_target_x = last_placed_main_stack_obj.region.x1
                        plug_target_y = last_placed_main_stack_obj.region.y1 - other_obj.height + 1
                    elif side_to_plug == "bottom":
                        plug_target_x = last_placed_main_stack_obj.region.x1
                        depth_of_new_tower = 0
                        for y, row in enumerate(reversed(range(last_placed_main_stack_obj.height))):
                            if all(last_placed_main_stack_obj.get(x, row) != last_placed_main_stack_obj.background_color for x in range(last_placed_main_stack_obj.width)):
                                depth_of_new_tower = y 
                                break
                        plug_target_y = last_placed_main_stack_obj.region.y2 - (depth_of_new_tower - 1)
                    elif side_to_plug == "left":
                        plug_target_x = last_placed_main_stack_obj.region.x1 - other_obj.width + idx
                        plug_target_y = last_placed_main_stack_obj.region.y1
                    elif side_to_plug == "right":
                        plug_target_x = last_placed_main_stack_obj.region.x2 + 1
                        plug_target_y = last_placed_main_stack_obj.region.y1

                    if plug_target_x != -1:
                        newly_plugged_object = place_object_on_new_grid(other_obj, plug_target_x, plug_target_y, result)
                        last_placed_main_stack_obj = newly_plugged_object
                        processed_other_indices.add(i)
                        plugged_in_this_iteration = True
                        break 
            if not plugged_in_this_iteration:
                break
    # 3. Place Remaining Other Objects on hole 2nd
    new_tower = None
    for hole_idx, next_hole in enumerate(holes):
        for obj_idx, other_obj in enumerate(flying_objects):
            if obj_idx in processed_other_indices:
                continue
            if is_vertical_docker:
                hole_side = 'left' if next_hole.region.x1 == docker_obj.region.x1 else 'right'
            else:
                hole_side = 'top' if next_hole.region.y1 == docker_obj.region.y1 else 'bottom'
            if (y_index := is_pluggable_object_to_hole(other_obj, next_hole, is_vertical_docker, hole_side)) == -1:
                continue

            def get_first_index_of_color(list, color):
                for i, item in enumerate(list):
                    if item != color:
                        return i
            if is_vertical_docker:
                x_index  = 0
                obj_first_col = [other_obj.get(0, y) for y in range(other_obj.height)]
                y_index = get_first_index_of_color(obj_first_col, other_obj.background_color)
            else:
                obj_first_row = [other_obj.get(x, 0) for x in range(other_obj.width)]
                x_index = get_first_index_of_color(obj_first_row, other_obj.background_color)
                y_index = 0
            new_tower = place_object_on_new_grid(other_obj, next_hole.region.x1 - x_index, next_hole.region.y1 - y_index, result)
            processed_other_indices.add(obj_idx)
            break
        if new_tower:
            break
    #  4: pluggable stacking
    while True:
        plugged_in_this_iteration = False
        for obj_idx, other_obj in enumerate(flying_objects):
            if obj_idx in processed_other_indices:
                continue
            side_to_plug, idx = is_pluggable_object(new_tower, other_obj, hole_side)
            if side_to_plug:
                plug_target_x, plug_target_y = -1, -1
                if side_to_plug == "top":
                    plug_target_x = new_tower.region.x1
                    plug_target_y = new_tower.region.y1 - other_obj.height
                elif side_to_plug == "bottom":
                    plug_target_x = new_tower.region.x1
                    depth_of_new_tower = 0
                    for y, row in enumerate(reversed(range(new_tower.height))): # from bottom to top
                        if all(new_tower.get(x, row) != new_tower.background_color for x in range(new_tower.width)):
                            depth_of_new_tower = y
                            break
                    plug_target_y = new_tower.region.y2 - (depth_of_new_tower - 1) # from top to bottom
                elif side_to_plug == "left":
                    if hole_side == 'left':
                        plug_target_x = new_tower.region.x1 - other_obj.width
                    else:
                        plug_target_x = new_tower.region.x2 - 1
                    plug_target_y = new_tower.region.y1
                elif side_to_plug == "right":
                    plug_target_x = new_tower.region.x2 - 1
                    plug_target_y = new_tower.region.y1
                # TODO:
                if plug_target_x != -1:
                    new_tower = place_object_on_new_grid(other_obj, plug_target_x, plug_target_y, result)
                    processed_other_indices.add(obj_idx)
                    plugged_in_this_iteration = True
                    break
        if not plugged_in_this_iteration:
            remaining_other_objects = [obj for obj_idx, obj in enumerate(flying_objects) if obj_idx not in processed_other_indices]
            break
    
        
    return result

if __name__ == "__main__":
    import os
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 16b78196 optimize_the_grid")

