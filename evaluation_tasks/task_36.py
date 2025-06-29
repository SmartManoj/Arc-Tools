import os
from collections import Counter
from arc_tools.grid import Color, Grid, SubGrid, detect_objects, GridRegion, GridPoint, place_object_on_new_grid
from arc_tools import logger
from arc_tools.plot import plot_grids
import json
def get_direction(side: str) -> tuple[int, int]:
    if side == 'top-left':
        return (-1, -1)
    elif side == 'top-right':
        return (1, -1)
    elif side == 'bottom-left':
        return (-1, 1)
    else: # bottom-right
        return (1, 1)
    
def cornerify(grid: Grid):
    '''
    dots is in black square frame.
    one dot is connected with an object.
    replicate the shape of the object with other dots.
    '''
    new_grid = grid.copy()
    black_frames = detect_objects(new_grid, required_color=Color.BLACK)
    # Find all single-pixel objects (dots)
    all_objects = detect_objects(new_grid, ignore_color=Color.BLACK)
    dots = [obj for obj in all_objects if len(obj.points) == 1]
    objects = [obj for obj in all_objects if len(obj.points) > 1]
    sample_obj = objects[0]
    # find the dot that is connected to the object by analyzing position with the black frame.
    def get_side(obj: GridRegion, frame: GridRegion):
        if obj.x1 < frame.x1 < obj.x2 and obj.y1 < frame.y1 < obj.y2:
            return 'top-left'
        elif obj.x1 < frame.x2 < obj.x2 and obj.y1 < frame.y1 < obj.y2:
            return 'top-right'
        elif obj.x1 < frame.x1 < obj.x2 and obj.y1 < frame.y2 < obj.y2:
            return 'bottom-left'
        elif obj.x1 < frame.x2 < obj.x2 and obj.y1 < frame.y2 < obj.y2:
            return 'bottom-right'
        else:
            return None
    for frame in black_frames:
        side = get_side(sample_obj.region, frame.region)
        if side == 'top-left':
            required_dot = GridPoint(sample_obj.region.x2, sample_obj.region.y2)
        elif side == 'top-right':
            required_dot = GridPoint(sample_obj.region.x1, sample_obj.region.y2)
        elif side == 'bottom-left':
            required_dot = GridPoint(sample_obj.region.x2, sample_obj.region.y1)
        elif side == 'bottom-right':
            required_dot = GridPoint(sample_obj.region.x1, sample_obj.region.y1)
        else:
            continue
        # check if required dot is background color, move one step to the side.
        if new_grid.get(required_dot.x, required_dot.y) == grid.background_color:
            direction = get_direction(side)
            required_dot = GridPoint(required_dot.x + direction[0], required_dot.y + direction[1])
        # find distance from required dot to the remaining dots in that object.
        distances = []
        for remaining_dot in sample_obj.points:
            if remaining_dot != required_dot:
                distance = required_dot.distance(remaining_dot)
                # neutralize the distance to bottom right.
                direction = get_direction(side)
                distance = ( distance[0] * direction[0], distance[1] * direction[1])
                distances.append(distance)
        break
    else:
        logger.info(f"Object at {sample_obj.region} is not connected to the frame.")
    # add the shape of the object to the other dots.
    def get_dot_side(dot: GridPoint, frame: GridRegion):
        top_left_distance = dot.manhattan_distance(GridPoint(frame.x1, frame.y1))
        top_right_distance = dot.manhattan_distance(GridPoint(frame.x2, frame.y1))
        bottom_left_distance = dot.manhattan_distance(GridPoint(frame.x1, frame.y2))
        bottom_right_distance = dot.manhattan_distance(GridPoint(frame.x2, frame.y2))
        min_distance = min(top_left_distance, top_right_distance, bottom_left_distance, bottom_right_distance)
        if min_distance == top_left_distance:
            return 'top-left'
        elif min_distance == top_right_distance:
            return 'top-right'
        elif min_distance == bottom_left_distance:
            return 'bottom-left'
        elif min_distance == bottom_right_distance:
            return 'bottom-right'
        else:
            return None
    for dot in dots:
        for frame in black_frames:
            dot_point = dot.points[0]
            # check if dot is in the frame.
            if not frame.region.contains(dot_point):
                continue
            # adjust for cropped frames.
            max_side = max(frame.width, frame.height)
            possible_points = [
                GridPoint(frame.region.x1, frame.region.y1),
                GridPoint(frame.region.x1 + max_side - 1, frame.region.y1),
                GridPoint(frame.region.x1, frame.region.y1 + max_side - 1),
                GridPoint(frame.region.x1 + max_side - 1, frame.region.y1 + max_side - 1)
            ]
            possible_frame_region = GridRegion(possible_points)
            side = get_dot_side(dot.points[0], possible_frame_region)
            if side:
                break
        else:
            continue
        
        direction = get_direction(side)
        for distance in distances:
            new_grid.set(dot.region.x1 - direction[0] * distance[0], dot.region.y1 - direction[1] * distance[1], dot.color)
    return new_grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 4c416de3 cornerify") 
