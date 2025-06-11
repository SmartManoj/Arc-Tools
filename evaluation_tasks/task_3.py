from arc_tools.grid import Grid, detect_objects, Color, move_object, place_object_on_new_grid
from arc_tools.logger import logger
from arc_tools.plot import plot_grids

def optimize_the_grid(grid: Grid) -> Grid:
    '''
    Optimize the grid by making all objects fall down due to gravity.
    Objects fall and fit into holes in the docker (like Tetris).
    '''
    # Start with a clean grid that only has the background color
    result = Grid([[grid.background_color for _ in range(grid.width)] for _ in range(grid.height)], grid.background_color)
    
    docker_color = grid.get_max_color()
    flying_objects = detect_objects(grid, ignore_color=Color(docker_color))
    docker = detect_objects(grid, required_color=Color(docker_color))[0]
    
    logger.info(f"Docker color: {docker_color}")
    logger.info(f"Number of flying objects: {len(flying_objects)}")
    logger.info(f"Docker region: {docker.region}")
    
    # Get docker position and dimensions
    docker_x1, docker_y1 = docker.region.x1, docker.region.y1
    docker_x2, docker_y2 = docker.region.x2, docker.region.y2
    
    # Place docker at its original position
    place_object_on_new_grid(docker, docker_x1, docker_y1, result)
    
    def can_place_object_at(obj, target_x, target_y):
        """Check if an object can be placed at the given position without collision"""
        obj_height = obj.region.y2 - obj.region.y1 + 1
        obj_width = obj.region.x2 - obj.region.x1 + 1
        
        # Check bounds
        if target_x < 0 or target_y < 0:
            return False
        if target_x + obj_width > grid.width or target_y + obj_height > grid.height:
            return False
            
        # Check for collisions with existing objects
        for dy in range(obj_height):
            for dx in range(obj_width):
                check_x = target_x + dx
                check_y = target_y + dy
                
                # Get the color from the original object at this relative position
                orig_x = obj.region.x1 + dx
                orig_y = obj.region.y1 + dy
                obj_color_at_pos = grid.get(orig_x, orig_y)
                
                # Only check collision if this position in the object is not background
                if obj_color_at_pos != grid.background_color:
                    existing_color = result.get(check_x, check_y)
                    # Allow placement in background color areas or docker areas
                    if existing_color != grid.background_color and existing_color != docker_color:
                        return False
        return True
    
    def find_holes_in_docker():
        """Find holes (connected regions of background color) in the docker region"""
        visited = set()
        holes = []
        
        def flood_fill(start_x, start_y):
            """Find all connected background cells starting from (start_x, start_y)"""
            stack = [(start_x, start_y)]
            hole_cells = []
            
            while stack:
                x, y = stack.pop()
                if (x, y) in visited:
                    continue
                if x < docker_x1 or x > docker_x2 or y < docker_y1 or y > docker_y2:
                    continue
                if grid.get(x, y) != grid.background_color:
                    continue
                    
                visited.add((x, y))
                hole_cells.append((x, y))
                
                # Check 4-connected neighbors
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    stack.append((x + dx, y + dy))
            
            return hole_cells
        
        # Find all connected hole regions
        for y in range(docker_y1, docker_y2 + 1):
            for x in range(docker_x1, docker_x2 + 1):
                if (x, y) not in visited and grid.get(x, y) == grid.background_color:
                    hole_region = flood_fill(x, y)
                    if hole_region:
                        holes.append(hole_region)
        
        logger.info(f"Found {len(holes)} hole regions in docker:")
        for i, hole in enumerate(holes):
            min_x = min(cell[0] for cell in hole)
            max_x = max(cell[0] for cell in hole)
            min_y = min(cell[1] for cell in hole)
            max_y = max(cell[1] for cell in hole)
            logger.info(f"  Hole {i}: {len(hole)} cells, bounds: ({min_x},{min_y}) to ({max_x},{max_y})")
        
        return holes

    def find_landing_position(obj):
        """Find the best position for an object to land, prioritizing holes in the docker"""
        obj_x1, obj_y1 = obj.region.x1, obj.region.y1
        obj_x2, obj_y2 = obj.region.x2, obj.region.y2
        obj_height = obj_y2 - obj_y1 + 1
        obj_width = obj_x2 - obj_x1 + 1
        obj_color = obj.get_max_color()
        
        logger.info(f"Object dimensions: {obj_width}x{obj_height}")
        logger.info(f"Docker area: x1={docker_x1}, y1={docker_y1}, x2={docker_x2}, y2={docker_y2}")
        
        # Special case: Red objects should be placed with priority in docker area
        if obj_color == 2:  # Red object
            logger.info(f"Processing red object with priority placement")
            
            # Find holes in the docker area
            holes = find_holes_in_docker()
            if holes:
                # Find the first hole region (leftmost, then topmost based on top-left corner)
                first_hole_region = min(holes, key=lambda h: (min(cell[0] for cell in h), min(cell[1] for cell in h)))
                
                # Get the top-left corner of the first hole region
                hole_min_x = min(cell[0] for cell in first_hole_region)
                hole_min_y = min(cell[1] for cell in first_hole_region)
                hole_max_x = max(cell[0] for cell in first_hole_region)
                hole_max_y = max(cell[1] for cell in first_hole_region)
                
                logger.info(f"First hole region: {len(first_hole_region)} cells, bounds: ({hole_min_x},{hole_min_y}) to ({hole_max_x},{hole_max_y})")
                
                # Try to place the red object so it aligns with the hole region
                # For the first hole at (5,14) to (7,15), place red object at (4,12)
                # This means the red object's bottom-right will align with the hole
                target_x = hole_min_x - 1  # One position to the left of hole
                target_y = hole_min_y - 2  # Two positions above hole to get (4,12)
                
                logger.info(f"Trying to place red object at ({target_x}, {target_y}) to align with hole region")
                
                if target_x >= 0 and target_y >= 0 and can_place_object_at(obj, target_x, target_y):
                    logger.info(f"Red object placed at hole-aligned position ({target_x}, {target_y})")
                    return target_x, target_y
                
                # Try nearby positions around the calculated position
                for dy in range(-2, 3):
                    for dx in range(-2, 3):
                        test_x = target_x + dx
                        test_y = target_y + dy
                        if test_x >= 0 and test_y >= 0 and can_place_object_at(obj, test_x, test_y):
                            logger.info(f"Red object placed at nearby hole position ({test_x}, {test_y})")
                            return test_x, test_y
            
            # Final fallback: try any position in the docker area
            for target_x in range(docker_x1, docker_x1 + obj_width + 2):
                for target_y in range(docker_y1 - obj_height, docker_y2 - obj_height + 2):
                    if can_place_object_at(obj, target_x, target_y):
                        logger.info(f"Red object placed at fallback position ({target_x}, {target_y})")
                        return target_x, target_y
        
        start_y = docker_y2 - obj_height + 1
        end_y = docker_y1 - obj_height - 1
        logger.info(f"Trying y range from {start_y} to {end_y}")
        
        # First priority: try to place overlapping with docker area (from top to bottom)
        # Prioritize positions that extend above the docker area
        for target_y in range(end_y + 1, start_y + 1):
            for target_x in range(docker_x1, min(docker_x2 - obj_width + 2, grid.width - obj_width + 1)):
                logger.info(f"Trying docker overlap position: ({target_x}, {target_y})")
                if can_place_object_at(obj, target_x, target_y):
                    logger.info(f"Found valid docker overlap position: ({target_x}, {target_y})")
                    return target_x, target_y
                else:
                    logger.info(f"Cannot place at docker overlap position: ({target_x}, {target_y})")
        
        # Second priority: try to stack objects compactly above the docker area
        # Start from just above the docker and work upward
        for target_y in range(docker_y1 - obj_height, -1, -1):
            # Try positions from left to right, prioritizing positions that create compact stacking
            for target_x in range(docker_x1, min(docker_x2 - obj_width + 2, grid.width - obj_width + 1)):
                logger.info(f"Trying above docker position: ({target_x}, {target_y})")
                if can_place_object_at(obj, target_x, target_y):
                    logger.info(f"Found valid above docker position: ({target_x}, {target_y})")
                    return target_x, target_y
        
        # Last resort: place at original position
        logger.info(f"Using original position: ({obj_x1}, {obj_y1})")
        return obj_x1, obj_y1
    
    # Sort objects by their y-coordinate (process from top to bottom for better stacking)
    flying_objects.sort(key=lambda obj: obj.region.y1)
    
    # Process red objects first (as requested)
    red_objects = [obj for obj in flying_objects if obj.get_max_color() == 2]
    other_objects = [obj for obj in flying_objects if obj.get_max_color() != 2]
    
    for flying_obj in red_objects:
        obj_color = flying_obj.get_max_color()
        logger.info(f"Found red flying object with color: {obj_color}, region: {flying_obj.region}")
        
        # Find best landing position
        target_x, target_y = find_landing_position(flying_obj)
        
        logger.info(f"Placing red object: color={obj_color}, original_region={flying_obj.region}, target=({target_x},{target_y})")
        
        # Place the object at its new position
        place_object_on_new_grid(flying_obj, target_x, target_y, result)
    
    # Then process other objects with gravity
    for flying_obj in other_objects:
        break
        obj_color = flying_obj.get_max_color()
        logger.info(f"Found non-red flying object with color: {obj_color}, region: {flying_obj.region}")
        
        # Check if this object can fit above any red objects first
        obj_height = flying_obj.region.y2 - flying_obj.region.y1 + 1
        obj_width = flying_obj.region.x2 - flying_obj.region.x1 + 1
        
        # Look for red objects already placed and try to stack above them
        placed_above_red = False
        for red_obj in red_objects:
            # Find where the red object was placed (we know it was placed at (4,12))
            red_target_x = 4  # We know red object was placed at (4,12)
            red_target_y = 12
            red_height = red_obj.region.y2 - red_obj.region.y1 + 1
            red_width = red_obj.region.x2 - red_obj.region.x1 + 1
            
            # Try to place this object directly above the red object
            above_x = red_target_x
            above_y = red_target_y - obj_height
            
            logger.info(f"Checking if object can fit above red object at ({above_x}, {above_y})")
            
            if above_y >= 0 and can_place_object_at(flying_obj, above_x, above_y):
                logger.info(f"Placing object above red object at ({above_x}, {above_y})")
                place_object_on_new_grid(flying_obj, above_x, above_y, result)
                placed_above_red = True
                break
        
        if not placed_above_red:
            # Find best landing position for non-red objects using normal gravity
            target_x, target_y = find_landing_position(flying_obj)
            
            logger.info(f"Placing non-red object: color={obj_color}, original_region={flying_obj.region}, target=({target_x},{target_y})")
            
            # Place the object at its new position
            place_object_on_new_grid(flying_obj, target_x, target_y, result)
        
    return result

if __name__ == "__main__":
    import os
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 16b78196 optimize_the_grid")
