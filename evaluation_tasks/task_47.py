import os
from arc_tools.grid import Grid, detect_objects, GridPoint
from arc_tools import logger
from arc_tools.plot import plot_grids



def construct_path(grid: Grid, starting_point: GridPoint, side: str,  point_color: int):
    if side == 'left':
        for x in range(starting_point.x):
            grid.set(x, starting_point.y, point_color)
    elif side == 'right':
        for x in range(starting_point.x + 1, grid.width):
            grid.set(x, starting_point.y, point_color)
    elif side == 'top':
        for y in range(starting_point.y):
            grid.set(starting_point.x, y, point_color)
    elif side == 'bottom':
        for y in range(starting_point.y + 1, grid.height):
            grid.set(starting_point.x, y, point_color)

def get_rotated_point(x, y, count, grid):
    if count == 1:
        x, y = y, grid.width - 1 - x
    elif count == 2:
        x, y = grid.width - 1 - x, grid.height - 1 - y
    elif count == 3:
        x, y = grid.height - 1 - y, x
    elif count == 0:
        pass
    return x, y

def parallel_universe(grid: Grid):
    '''
    Create parallel universe paths from isolated colored dots.
    Preserves original input and adds selective magenta lines.
    '''
    # Start with the original grid
    result = grid.copy()
    
    # Find isolated colored dots (single pixels that are not part of larger structures)
    objects = detect_objects(grid)
    starting_points = []
    parallel_universes = []
    for object in objects:
        if object.area == 1:
            starting_points.append(object.points[0])
        else:
            parallel_universes.append(object)

    # draw lines from starting points
    for point in starting_points:
        point_color = grid[point.y][point.x]
        
        # Determine direction based on point position
        if point.x == 0:
            direction = 'right'
        elif point.x == grid.width - 1:
            direction = 'left'
        elif point.y == 0:
            direction = 'down'
        elif point.y == grid.height - 1:
            direction = 'up'
        else:
            continue  # Skip points not on edges
        
        # Draw line in the determined direction until meeting a parallel universe
        if direction == 'right':
            for x in range(point.x, grid.width):
                if x != point.x and result.get(x, point.y) != grid.background_color:
                    meeting_point = GridPoint(x, point.y)
                    break
                result.set(x, point.y, point_color)
        elif direction == 'left':
            for x in reversed(range(point.x + 1)):
                if x != point.x and result.get(x, point.y) != grid.background_color:
                    meeting_point = GridPoint(x, point.y)
                    break
                result.set(x, point.y, point_color)
        elif direction == 'down':
            for y in range(point.y, grid.height):
                if y != point.y and result.get(point.x, y) != grid.background_color:
                    meeting_point = GridPoint(point.x, y)
                    break
                result.set(point.x, y, point_color)
        elif direction == 'up':
            for y in reversed(range(point.y + 1)):
                if y != point.y and result.get(point.x, y) != grid.background_color:
                    meeting_point = GridPoint(point.x, y)
                    break
                result.set(point.x, y, point_color)
        
        # Find which parallel universe contains the meeting point
        matched_parallel_universe = None
        for parallel_universe in parallel_universes:
            if parallel_universe.contains(meeting_point):
                matched_parallel_universe = parallel_universe
                break
        
        if matched_parallel_universe is None:
            continue
            
        # Calculate relative position of meeting point within the matched parallel universe
        meeting_point_offset = (
            meeting_point.x - matched_parallel_universe.region.x1,
            meeting_point.y - matched_parallel_universe.region.y1
        )
        flipped_meeting_point_offset = (
            matched_parallel_universe.width - 1 - meeting_point_offset[0],
            meeting_point_offset[1]
        )
        # Find corresponding points in other parallel universes
        for other_universe in parallel_universes:
            if other_universe == matched_parallel_universe:
                continue
                
            # Try different rotations and reflections to find matching universe
            test_universe = other_universe.copy()
            
            for rotation_count in range(4):
                # Check if universes match after rotation
                if test_universe.is_similar(matched_parallel_universe):
                    # Calculate corresponding point in this universe
                    
                    new_offset = get_rotated_point(meeting_point_offset[0], meeting_point_offset[1], rotation_count, test_universe)
                    new_starting_point = GridPoint(
                        new_offset[0] + other_universe.region.x1,
                        new_offset[1] + other_universe.region.y1
                    )
                    
                    # Determine direction for new starting point
                    if new_starting_point.x == other_universe.region.x1:
                        construct_path(result, new_starting_point, 'left', point_color)
                    elif new_starting_point.x == other_universe.region.x2:
                        construct_path(result, new_starting_point, 'right', point_color)
                    elif new_starting_point.y == other_universe.region.y1:
                        construct_path(result, new_starting_point, 'top', point_color)
                    elif new_starting_point.y == other_universe.region.y2:
                        construct_path(result, new_starting_point, 'bottom', point_color)
                    break
                    
                # Try with vertical flip
                flipped_universe = test_universe.flip_vertically()
                if flipped_universe.is_similar(matched_parallel_universe):
                    # Calculate corresponding point in flipped universe
                    new_offset = get_rotated_point(flipped_meeting_point_offset[0], flipped_meeting_point_offset[1], rotation_count, flipped_universe)
                    

                    new_starting_point = GridPoint(
                        new_offset[0] + other_universe.region.x1,
                        new_offset[1] + other_universe.region.y1
                    )
                    
                    # Determine direction for new starting point
                    if new_starting_point.x == other_universe.region.x1:
                        construct_path(result, new_starting_point, 'left', point_color)
                    elif new_starting_point.x == other_universe.region.x2:
                        construct_path(result, new_starting_point, 'right', point_color)
                    elif new_starting_point.y == other_universe.region.y1:
                        construct_path(result, new_starting_point, 'top', point_color)
                    elif new_starting_point.y == other_universe.region.y2:
                        construct_path(result, new_starting_point, 'bottom', point_color)
                    break
                    
                # Rotate for next iteration
                test_universe = test_universe.rotate()

    return result

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 64efde09 parallel_universe") 
