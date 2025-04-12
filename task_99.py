from itertools import combinations
from arc_tools.logger import logger
from arc_tools.grid import Grid, GridPoint, detect_objects, SubGrid
from arc_tools.grid import detect_objects, move_object
from arc_tools.plot import plot_grids

def calculate_offset(A1: GridPoint, A2: GridPoint): 
    # calculate offset between A1 and A2
    offset_x = A1.x - A2.x
    offset_y = A1.y - A2.y
    return offset_x, offset_y

def check_fit_recursive(current_grid: Grid, remaining_objects: list[SubGrid], locked_dots_so_far: list[GridPoint], dot_value: int):
    """
    Recursively tries to fit objects onto the grid.

    Args:
        current_grid: The current state of the grid (list of lists).
        remaining_objects: A list of SubGrid instances yet to be placed.
        locked_dots_so_far: A list of GridPoint instances on the centre object
                           that are already used for fitting.

    Returns:
        A tuple (final_grid, success_boolean).
        final_grid is the grid state after attempting fits.
        success_boolean is True if all objects were successfully fitted, False otherwise.
    """
    global plot_show
    # Base Case: No more objects to fit, success!
    if not remaining_objects:
        logger.debug("All objects successfully fitted.")
        return current_grid, True
    logger.debug(f"Locked dots so far: {locked_dots_so_far}")
    for obj_id, current_obj in enumerate(remaining_objects):
        # current_grid = deepcopy(initial_grid)
        rest_objects = [obj for i, obj in enumerate(remaining_objects) if i != obj_id]
        # Detect the main structure (centre object) in the *current* grid state
        # Assumes the largest or first detected object is the centre one.
        detected_centre_objects = detect_objects(current_grid)
        if not detected_centre_objects:
            logger.error("No centre object detected in the current grid state. Cannot proceed.")
            return current_grid, False
        centre_object = detected_centre_objects[0] # Assuming the first one is the target

        centre_object_dots_position_and_sides = centre_object.get_points_and_sides_of_dots(dot_value)
        obj_dots_position_and_sides = current_obj.get_points_and_sides_of_dots(dot_value)

        logger.debug(f"Attempting to fit object {current_obj.region} ({len(rest_objects)} total remaining).")
        

        centre_object_dots_position_and_sides =[i for i in centre_object_dots_position_and_sides if i[0] not in locked_dots_so_far]
        def obj_side_fully_matches_with_centre_object_side(so, sc):
            '''Only matches if there is a side in so that is in sc'''
            return so and all(side in sc for side in so) 

        # Iterate through combinations of points to find a valid fit
        if len(obj_dots_position_and_sides) == 1:
            obj_dots_position_and_sides *= 2
        if len(centre_object_dots_position_and_sides) == 1:
            centre_object_dots_position_and_sides *= 2
        for psc1, psc2 in combinations(centre_object_dots_position_and_sides, 2):
            for pso1, pso2 in combinations(obj_dots_position_and_sides, 2):
                # logger.debug(f"Checking combination: psc1={psc1}, psc2={psc2}, pso1={pso1}, pso2={pso2}")

                # Skip based on side compatibility (same logic as original)
                # Ensure sides are compatible for potential alignment. If all sides of b1 are in a1's sides,
                # it implies b1 is potentially on the same edge/corner as a1, which might prevent proper alignment check based on two points.
                # This condition might need review based on the exact fitting logic desired.
                # if ((not pso1[1] and not psc1[1]) or (all(side in pso1[1] for side in psc1[1]))) and ((not pso2[1] and not psc2[1]) or (all(side in pso2[1] for side in psc2[1]))):
                    # continue
                if obj_side_fully_matches_with_centre_object_side(pso1[1], psc1[1]) or obj_side_fully_matches_with_centre_object_side(pso2[1], psc2[1]):
                    continue
                a1, a2, b1, b2 = psc1[0], psc2[0], pso1[0], pso2[0]
                offset_x1, offset_y1 = calculate_offset(a1, b1)
                offset_x2, offset_y2 = calculate_offset(a2, b2)

                # Check for matching offsets and if points are not already locked
                if offset_x1 == offset_x2 and offset_y1 == offset_y2 and \
                a1 not in locked_dots_so_far and a2 not in locked_dots_so_far:

                    logger.debug(f"Found potential fit for object {current_obj.region} at offset ({offset_x1}, {offset_y1}). Locking points {a1}, {a2}.")

                    # Create a new grid state by applying the move
                    # Use deepcopy to avoid modifying the grid state needed for backtracking
                    new_grid = current_grid.copy()
                    new_grid = move_object(current_obj, offset_x1, offset_y1, new_grid) # move_object modifies new_grid in place

                    # Update locked dots for the next recursive call
                    new_locked_dots = locked_dots_so_far + [a1, a2] 

                    # Recurse with the updated state
                    final_grid, success = check_fit_recursive(new_grid, rest_objects, new_locked_dots, dot_value)

                    # If the recursive call was successful, propagate the success upwards
                    if success:
                        return final_grid, True

                    # If the recursive call failed (returned False), it means this fit didn't lead
                    # to a solution. We implicitly backtrack by continuing the loops
                    # to find another potential fit for the *current* object.
                    logger.debug(f"Recursive call failed after fitting object {current_obj.region} with offset ({offset_x1}, {offset_y1}). Backtracking/Trying next combination.")


        # If all combinations for the current object have been tried and none led to a solution
        logger.debug(f"Could not find a valid fit")
        logger.debug(f"Centre object points: {centre_object_dots_position_and_sides}")
        logger.debug(f"Current object points: {obj_dots_position_and_sides}")
        
    return current_grid, False # Indicate failure for this path

def check_fit(grid: Grid) -> Grid:
    '''
    1. orange dot is the min value of the object.
    2. yellow is the centre object? (or no hollow object with no orange dot at corners) or both?
    3. move other objects to the yellow object by matching with the dot.
    '''
    initial_grid = grid.copy()
    objects = detect_objects(grid)
    logger.debug(f"Total objects: {len(objects)}")
    for obj in objects:
        if not obj.has_hollow_space()  and obj.has_yellow_block():
            centre_object = obj
            break
    dot_value = centre_object.get_min_value()
    output = centre_object.get_full_grid()
    objects.remove(centre_object)
    
    
    logger.info("New count of objects: %d", len(objects))
    # Initial call to the recursive function with an empty list for locked_dots
    output, is_fitted = check_fit_recursive(output, objects, [], dot_value)
    if is_fitted:
        return output
    else:
        return initial_grid


if __name__ == "__main__":
    import os
    os.system("main.py cbebaa4b check_fit")

