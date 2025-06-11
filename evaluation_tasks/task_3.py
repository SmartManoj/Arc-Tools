from arc_tools.grid import Grid, detect_objects, Color, move_object, place_object_on_new_grid, GridRegion, GridPoint, SubGrid
from arc_tools.logger import logger
from arc_tools.plot import plot_grids

def is_pluggable(list_1, list_2):
    '''
    Check if list_1 and list_2 are pluggable by xor and sum is 1.
    '''
    return sum(a != b for a, b in zip(list_1, list_2)) == len(list_1)

def is_pluggable_object(obj_1, obj_2):
    '''
    Check if obj_2 can be placed on which side of obj_1.
    obj_1 is assumed to be an object already placed on a grid (e.g., the result grid).
    obj_2 is an object from the original set of flying objects.
    Their solidity is determined by their respective parent_grid.background_color.
    '''
    # Background color for obj_1 (e.g., from result grid)
    bg_color_obj_1 = obj_1.parent_grid.background_color 
    # Background color for obj_2 (e.g., from original input grid)
    bg_color_obj_2 = obj_2.parent_grid.background_color

    if obj_1.width == obj_2.width:
        obj_1_top_row = [obj_1.get(x, 0) != bg_color_obj_1 for x in range(obj_1.width)]
        obj_2_bottom_row = [obj_2.get(x, obj_2.height - 1) != bg_color_obj_2 for x in range(obj_2.width)]
        
        if is_pluggable(obj_1_top_row, obj_2_bottom_row):
            return "top"
        
        obj_1_bottom_row = [obj_1.get(x, obj_1.height - 1) != bg_color_obj_1 for x in range(obj_1.width)]
        obj_2_top_row = [obj_2.get(x, 0) != bg_color_obj_2 for x in range(obj_2.width)]
        if is_pluggable(obj_1_bottom_row, obj_2_top_row):
            return "bottom"
            
    if obj_1.height == obj_2.height:
        obj_1_left_col = [obj_1.get(0, y) != bg_color_obj_1 for y in range(obj_1.height)]
        obj_2_right_col = [obj_2.get(obj_2.width - 1, y) != bg_color_obj_2 for y in range(obj_2.height)]
        if is_pluggable(obj_1_left_col, obj_2_right_col):
            return "left"
            
        obj_1_right_col = [obj_1.get(obj_1.width - 1, y) != bg_color_obj_1 for y in range(obj_1.height)]
        obj_2_left_col = [obj_2.get(0, y) != bg_color_obj_2 for y in range(obj_2.height)]
        if is_pluggable(obj_1_right_col, obj_2_left_col):
            return "right"
    return None
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

def optimize_the_grid(grid: Grid) -> Grid:
    result = Grid([[grid.background_color for _ in range(grid.width)] for _ in range(grid.height)], grid.background_color)
    
    docker_color_val = grid.get_max_color()
    flying_objects = detect_objects(grid, ignore_color=Color(docker_color_val))
    docker_obj = detect_objects(grid, required_color=Color(docker_color_val))[0]
    holes = get_docker_inner_holes(docker_obj)
    # sort by size
    holes.sort(key=lambda x: x.width * x.height, reverse=True)
    for hole in holes:
        logger.info(f"Hole: {hole}")
    hole_count = len(holes)
    # find the best landing position for the docker object
    logger.info(f"Input grid: {grid.width}x{grid.height}, Docker color: {docker_color_val}")
    logger.info(f"Found {len(flying_objects)} flying objects.")
    logger.info(f"Docker object original region: {docker_obj.region}")
    
    place_object_on_new_grid(docker_obj, docker_obj.region.x1, docker_obj.region.y1, result)

    def can_place_object_at(obj_to_place, target_x, target_y, on_grid):
        obj_h = obj_to_place.height
        obj_w = obj_to_place.width

        if target_x < 0 or target_y < 0 or \
           target_x + obj_w > on_grid.width or \
           target_y + obj_h > on_grid.height:
            return False
        
        obj_own_background_color = obj_to_place.parent_grid.background_color
        
        for dy_obj in range(obj_h):
            for dx_obj in range(obj_w):
                obj_pixel = obj_to_place.get(dx_obj, dy_obj)
                if obj_pixel != obj_own_background_color: 
                    world_x = target_x + dx_obj
                    world_y = target_y + dy_obj
                    if on_grid.get(world_x, world_y) != on_grid.background_color:
                        return False
        return True

    def get_original_docker_hole_cells(original_input_grid, docker_object_from_original):
        hole_cells = set()
        holes = get_docker_inner_holes(docker_object_from_original)
        for hole in holes:
            for x in range(hole.region.x1, hole.region.x2 + 1):
                for y in range(hole.region.y1, hole.region.y2 + 1):
                    hole_cells.add((x, y))
        logger.info(f"Identified {len(hole_cells)} original docker hole cells.")
        return hole_cells

    all_original_docker_hole_cells = get_original_docker_hole_cells(grid, docker_obj)

    def find_landing_position_scored(obj_to_land, current_result_grid, original_grid_for_context, 
                                     original_hole_cells_set):
        obj_h = obj_to_land.height
        obj_w = obj_to_land.width
        obj_max_c = obj_to_land.get_max_color() # Corrected
        obj_own_bg_color = obj_to_land.parent_grid.background_color

        logger.info(f"Finding scored landing for obj color {obj_max_c} (region {obj_to_land.region}), dims {obj_w}x{obj_h}")
        
        potential_landings = []
        for tx in range(original_grid_for_context.width - obj_w + 1):
            lowest_y_stable = -1
            for ty in range(original_grid_for_context.height - obj_h + 1):
                if can_place_object_at(obj_to_land, tx, ty, current_result_grid):
                    is_at_bottom = (ty + obj_h == original_grid_for_context.height)
                    is_supported = False
                    if not is_at_bottom:
                        if not can_place_object_at(obj_to_land, tx, ty + 1, current_result_grid):
                            is_supported = True
                    
                    if is_at_bottom or is_supported:
                        lowest_y_stable = ty
                        break 
            
            if lowest_y_stable != -1:
                # Reverted hole_score: count actual overlap of object's solid pixels with original hole cells
                hole_score = 0
                for dy_o in range(obj_h):
                    for dx_o in range(obj_w):
                        obj_pixel = obj_to_land.get(dx_o, dy_o)
                        if obj_pixel != obj_own_bg_color: # Solid part of object
                            world_x_coord = tx + dx_o
                            world_y_coord = lowest_y_stable + dy_o
                            if (world_x_coord, world_y_coord) in original_hole_cells_set:
                                hole_score += 1
                                
                potential_landings.append({
                    'x': tx,
                    'y': lowest_y_stable,
                    'obj_bottom_y': lowest_y_stable + obj_h - 1,
                    'hole_score': hole_score # Use the pixel-overlap hole score
                })

        if not potential_landings:
            logger.warning(f"No landing spot found for obj {obj_to_land.region} (color {obj_max_c}). Using its original position: ({obj_to_land.region.x1}, {obj_to_land.region.y1})")
            return obj_to_land.region.x1, obj_to_land.region.y1

        potential_landings.sort(key=lambda spot: (-spot['hole_score'], -spot['obj_bottom_y'], spot['x']))
        
        best_landing = potential_landings[0]
        logger.info(f"Best landing for obj {obj_to_land.region} (color {obj_max_c}): ({best_landing['x']}, {best_landing['y']}) "
                    f"(bottom_y {best_landing['obj_bottom_y']}, hole_score {best_landing['hole_score']})")
        return best_landing['x'], best_landing['y']

    flying_objects.sort(key=lambda obj_item: (obj_item.region.y1, obj_item.region.x1))

    red_objects = [obj for obj in flying_objects if obj.get_max_color() == 2] # Corrected
    other_objects_list = [obj for obj in flying_objects if obj.get_max_color() != 2] # Corrected
    
    last_placed_main_stack_obj = None

    # 1. Place Red Objects
    for r_obj in red_objects:
        r_tx, r_ty = find_landing_position_scored(r_obj, result, grid, all_original_docker_hole_cells)
        logger.info(f"Placing RED obj {r_obj.region} at ({r_tx},{r_ty})")
        placed_r_obj_instance = place_object_on_new_grid(r_obj, r_tx, r_ty, result)
        last_placed_main_stack_obj = placed_r_obj_instance 
    
    # 2. Pluggable Stacking
    processed_other_indices = set()
    if last_placed_main_stack_obj:
        logger.info(f"Starting pluggable stacking on base: {last_placed_main_stack_obj.region}")
        while True:
            plugged_in_this_iteration = False
            for i, other_obj in enumerate(other_objects_list):
                if i in processed_other_indices:
                    continue
                
                side_to_plug = is_pluggable_object(last_placed_main_stack_obj, other_obj)
                
                if side_to_plug:
                    logger.info(f"Attempting to plug {other_obj.region} (idx {i}, color {other_obj.get_max_color()}) " # Corrected
                                f"to {last_placed_main_stack_obj.region} on side '{side_to_plug}'")
                    
                    plug_target_x, plug_target_y = -1, -1
                    if side_to_plug == "top":
                        plug_target_x = last_placed_main_stack_obj.region.x1
                        plug_target_y = last_placed_main_stack_obj.region.y1 - other_obj.height
                    elif side_to_plug == "bottom":
                        plug_target_x = last_placed_main_stack_obj.region.x1
                        plug_target_y = last_placed_main_stack_obj.region.y2 + 1
                    elif side_to_plug == "left":
                        plug_target_x = last_placed_main_stack_obj.region.x1 - other_obj.width
                        plug_target_y = last_placed_main_stack_obj.region.y1
                    elif side_to_plug == "right":
                        plug_target_x = last_placed_main_stack_obj.region.x2 + 1
                        plug_target_y = last_placed_main_stack_obj.region.y1

                    if plug_target_x != -1 and \
                       can_place_object_at(other_obj, plug_target_x, plug_target_y, result):
                        logger.info(f"  Plugging {other_obj.region} at ({plug_target_x},{plug_target_y})")
                        newly_plugged_object = place_object_on_new_grid(other_obj, plug_target_x, plug_target_y + 1, result)
                        last_placed_main_stack_obj = newly_plugged_object
                        processed_other_indices.add(i)
                        plugged_in_this_iteration = True
                        break 
                    else:
                        logger.info(f"  Cannot plug {other_obj.region} at ({plug_target_x},{plug_target_y}). Collision or invalid side.")
            
            if not plugged_in_this_iteration:
                logger.info("No more objects could be plugged in this iteration.")
                break 
    else:
        logger.info("No base object for pluggable stacking (no red objects placed or none suitable).")

    # 3. Place Remaining Other Objects
    logger.info("Placing remaining 'other' objects by scored gravity...")
    for i, other_obj in enumerate(other_objects_list):
        break
        if i in processed_other_indices:
            continue
        
        o_tx, o_ty = find_landing_position_scored(other_obj, result, grid, all_original_docker_hole_cells)
        logger.info(f"Placing OTHER obj {other_obj.region} (color {other_obj.get_max_color()}) at ({o_tx},{o_ty})") # Corrected
        place_object_on_new_grid(other_obj, o_tx, o_ty, result)
        
    return result

if __name__ == "__main__":
    import os
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 16b78196 optimize_the_grid")

