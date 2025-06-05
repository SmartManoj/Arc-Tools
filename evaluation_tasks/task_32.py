import os
from collections import Counter
from arc_tools.grid import Color, Grid, SubGrid, detect_objects, GridRegion, GridPoint, place_object_on_new_grid

def remove_marker(obj: SubGrid, clue_piece_color: Color):
    # check topleft corner
    grid = obj.parent_grid
    x1, y1, x2, y2 = obj.region.x1, obj.region.y1, obj.region.x2, obj.region.y2
    
    # Initialize default values
    frame_color = None
    corner = None
    
    if obj[0][0] == clue_piece_color:
        grid[y1][x1] = obj.background_color
        grid[y1][x1 + 1] = obj.background_color
        grid[y1 + 1][x1] = obj.background_color
        x1 += 1
        y1 += 1
        frame_color = grid[y1][x1]
        corner = 'top_left'
    # check topright corner
    elif obj[0][obj.width - 1] == clue_piece_color:
        grid[y1][x2] = obj.background_color
        grid[y1][x2 - 1] = obj.background_color
        grid[y1 + 1][x2] = obj.background_color
        x2 -= 1
        y1 += 1
        frame_color = grid[y1][x2]
        corner = 'top_right'
    # check bottomleft corner
    elif obj[obj.height - 1][0] == clue_piece_color:
        grid[y2][x1] = obj.background_color
        grid[y2][x1 + 1] = obj.background_color
        grid[y2 - 1][x1] = obj.background_color
        x1 += 1
        y2 -= 1
        frame_color = grid[y2][x1]
        corner = 'bottom_left'
    # check bottomright corner
    elif obj[obj.height - 1][obj.width - 1] == clue_piece_color:
        grid[y2][x2] = obj.background_color
        grid[y2][x2 - 1] = obj.background_color
        grid[y2 - 1][x2] = obj.background_color
        x2 -= 1
        y2 -= 1
        frame_color = grid[y2][x2]
        corner = 'bottom_right'
    
    return SubGrid(GridRegion([GridPoint(x1, y1), GridPoint(x2, y2)]), grid), corner, frame_color

def match_border(obj: SubGrid, static_region: dict, side: str, for_border: str|None = None):
    ''' Compare borders between obj and static_obj based on the specified side.'''
    grid = obj.parent_grid
    static_grid = static_region['grid']
    fcs = {static_region['frame_color']}
    if side == 'top':
        # For top side: compare obj top border with static_obj bottom border
        obj_top_border = [grid[obj.region.y1][col] for col in range(obj.region.x1, obj.region.x2+1)]
        if len(set(obj_top_border)) == 1:
            return False, (None, None)
        # if static_region['bottom'] is background color, go up to find the next non-background color, then check the next len(obj_top_border) cells of static_bottom_border and return that x value.
        required_length = len(obj_top_border)
        is_matched = False
        for x in range(static_region['left'], static_region['right']+1):
            for y in range(static_region['bottom'], static_region['top']+1, -1):
                if static_grid[y][x] != static_grid.background_color:
                    static_bottom_border = [static_grid[y][x + col] for col in range(required_length) if x + col <= static_region['right']]
                    is_matched = all(obj_color == static_color for obj_color, static_color in zip(obj_top_border, static_bottom_border)) and set(static_bottom_border) != fcs
                    break
            if is_matched:
                break
        return is_matched, (x, y + 1)
    elif side == 'bottom':
        # For bottom side: compare obj bottom border with static_obj top border
        obj_bottom_border = [grid[obj.region.y2][col] for col in range(obj.region.x1, obj.region.x2+1)]
        if len(set(obj_bottom_border)) == 1:
            return False, (None, None)
        # if static_region['top'] is background color, go up to find the next non-background color, then check the next len(obj_bottom_border) cells of static_top_border and return that x value.
        required_length = len(obj_bottom_border)
        is_matched = False
        for x in range(static_region['left'], static_region['right']+1):
            for y in range(static_region['top'], static_region['bottom']+1):
                if static_grid[y][x] != static_grid.background_color:
                    static_top_border = [static_grid[y][x + col] for col in range(required_length) if x + col <= static_region['right']]
                    is_matched = all(obj_color == static_color for obj_color, static_color in zip(obj_bottom_border, static_top_border)) and set(static_top_border) != fcs
                    break
            if is_matched:
                break
        return is_matched, (x, y - obj.height)
    elif side == 'left':
        # For left side: compare obj left border with static_obj right border
        obj_left_border = [grid[row][obj.region.x1] for row in range(obj.region.y1, obj.region.y2+1) if grid[row][obj.region.x1] != grid.background_color]
        if len(set(obj_left_border)) == 1:
            return False, (None, None)
        # if static_region['right'] is background color, go left to find the next non-background color, then check the next len(obj_left_border) cells of static_right_border and return that y value.
        required_length = len(obj_left_border)
        is_matched = False
        for y in range(static_region['top'], static_region['bottom']+1):
            for x in range(static_region['right'], static_region['left']-1, -1):
                if static_grid[y][x] != static_grid.background_color:
                    static_right_border = [static_grid[y + row][x] for row in range(required_length) if y + row <= static_region['bottom'] and static_grid[y + row][x+1] == static_grid.background_color]
                    if len(static_right_border) != required_length or not static_right_border:
                        continue
                    is_matched = all(obj_color == static_color for obj_color, static_color in zip(obj_left_border, static_right_border)) and set(static_right_border) != fcs
                    if for_border == 'bottom':
                        is_matched = is_matched and y + required_length - 1 == static_region['bottom']
                    if for_border == 'right':
                        is_matched = is_matched and x + obj.width  == static_region['right']
                    if for_border == 'top':
                        is_matched = is_matched and y == static_region['top']
                    break
            if is_matched:
                break
        return is_matched, (x + 1, y)
    elif side == 'right':
        # For right side: compare obj right border with static_obj left border
        obj_right_border = [grid[row][obj.region.x2] for row in range(obj.region.y1, obj.region.y2+1)]
        if len(set(obj_right_border)) == 1:
            return False, (None, None)
        # if static_region['left'] is background color, go right to find the next non-background color, then check the next len(obj_right_border) cells of static_left_border and return that y value.
        required_length = len(obj_right_border)
        is_matched = False
        def is_sublist(main_list, sublist):
            for i in range(len(main_list) - len(sublist) + 1):
                if main_list[i:i+len(sublist)] == sublist:
                    return i
            return 0
        for y in range(static_region['top'], static_region['bottom']+1):
            for x in range(static_region['left'], static_region['right']+1):
                if static_grid[y][x] != static_grid.background_color:
                    static_left_border = [static_grid[y + row][x] for row in range(required_length) if y + row <= static_region['bottom']]
                    if len(static_left_border) != required_length:
                        min_top = static_region.get('min_top')
                        if (shift := is_sublist(obj_right_border, static_left_border))!=0 and y <= static_region['top'] and (min_top is None or y - shift >= min_top):
                            y -= shift
                            obj_right_border = obj_right_border[shift:]
                        else:
                            continue
                    is_matched = all(obj_color == static_color for obj_color, static_color in zip(obj_right_border, static_left_border)) and set(static_left_border) != fcs
                    break
            if is_matched:
                break
        return is_matched, (x - obj.width, y)
    return False, (None, None)

def join_the_frame(grid: Grid):
    '''
    1. First move object 2 to above object 4 and object 3 to left of object 4
    2. Connect all objects with orange color
    3. Remove the yellow color
    '''
    def remove_object(obj: SubGrid):
        grid.remove_object(obj)
        remaining_objects.remove(obj)

    def set_value_for(side: str, value):
        if side == 'top':
            first_value = min(static_region['top'], value)
            second_value = max(first_value, 0)
        elif side == 'bottom':
            first_value = max(static_region['bottom'], value)
            second_value = min(first_value, grid.height - 1)
        elif side == 'left':
            first_value = min(static_region['left'], value)
            second_value = max(first_value, 0)
        elif side == 'right':
            first_value = max(static_region['right'], value)
            second_value = min(first_value, grid.width - 1)
        return second_value
    result = grid.get_frame()
    
    # Detect all objects in the grid
    objects = detect_objects(grid)
    # find the object with yellow color
    for obj in objects:
        corner_colors = set(obj.get_corner_colors())
        if len(corner_colors) > 2:
            static_object = obj
            possible_clue_piece_colors = corner_colors - {obj.color, grid.background_color}
            if len(possible_clue_piece_colors) == 1:
                clue_piece_color = possible_clue_piece_colors.pop()
            else:
                color_count = Counter(obj.get_values_count())
                for color in possible_clue_piece_colors:
                    if color_count[color] == 3:
                        clue_piece_color = color
                        break

            break
    remaining_objects = [obj for obj in objects if obj != static_object]

    static_object, corner, frame_color = remove_marker(static_object, clue_piece_color)
    place_object_on_new_grid(static_object, static_object.region.x1, static_object.region.y1, result)
    static_region = {'top': static_object.region.y1, 'bottom': static_object.region.y2, 'left': static_object.region.x1, 'right': static_object.region.x2, 'grid': result, 'frame_color': frame_color}
    if corner == 'top_right':
        static_region['min_top'] = static_region['top']
        static_region['max_right'] = static_region['right']
    elif corner == 'bottom_right':
        static_region['max_bottom'] = static_region['bottom']
        static_region['max_right'] = static_region['right']
    elif corner == 'bottom_left':
        static_region['max_bottom'] = static_region['bottom']
        static_region['min_left'] = static_region['left']
    elif corner == 'top_left':
        static_region['min_top'] = static_region['top']
        static_region['min_left'] = static_region['left']
    left_border_objects = []
    bottom_border_objects = []
    top_border_objects = []
    right_border_objects = []
    for obj in remaining_objects[:]:
        if all(obj[row][0] == frame_color for row in range(obj.height)):
            left_border_objects.append(obj)
        if all(obj[obj.height - 1][col] == frame_color for col in range(obj.width)):
            bottom_border_objects.append(obj)
        if all(obj[row][obj.width - 1] == frame_color for row in range(obj.height)):
            right_border_objects.append(obj)
        if all(obj[0][col] == frame_color for col in range(obj.width)):
            top_border_objects.append(obj)
    border_objects = {
        'left': left_border_objects,
        'bottom': bottom_border_objects,
        'top': top_border_objects,
        'right': right_border_objects,
        'all': remaining_objects,
    }
    border_order = [i for i in corner.split('_')]
    for border in border_objects:
        if border not in border_order:
            border_order.append(border)
    for border in border_order:
        ro = border_objects[border]
        len_ro = len(ro)
        for _ in range(len_ro):
            placed = False
            for obj in ro[:]:
                if obj not in ro:
                    continue
                if border == 'all' and obj not in remaining_objects:
                    continue
                
                # tell which border has non-frame color
                possible_sides = []
                if any(obj[0][col] not in (frame_color, obj.background_color) for col in range(obj.width)):
                    possible_sides.append('top')
                if any(obj[obj.height - 1][col] not in (frame_color, obj.background_color) for col in range(obj.width)):
                    possible_sides.append('bottom')
                if any(obj[row][0] not in (frame_color, obj.background_color) for row in range(obj.height)):
                    possible_sides.append('left')
                if any(obj[row][obj.width - 1] not in (frame_color, obj.background_color) for row in range(obj.height)):
                    possible_sides.append('right')
                for side in possible_sides:
                    is_matched, (x, y) = match_border(obj, static_region, side, for_border=border)
                    if is_matched:
                        if side == 'left':
                            static_region['right'] = set_value_for('right', x + obj.width - 1)
                            static_region['top'] = set_value_for('top', y)
                        elif side == 'right':
                            static_region['left'] = set_value_for('left', x)
                            static_region['top'] = set_value_for('top', y)
                        elif side == 'top':
                            static_region['bottom'] = set_value_for('bottom', y + obj.height - 1)
                            static_region['right'] = set_value_for('right', x + obj.width - 1)
                        elif side == 'bottom':
                            static_region['top'] = set_value_for('top', y)
                            static_region['right'] = set_value_for('right', x + obj.width - 1)
                        place_object_on_new_grid(obj, x, y, result)
                        remove_object(obj)
                        if obj in ro: 
                            ro.remove(obj)
                        placed = True
                        break
            if not placed:
                break
            

    grid.remove_object(static_object)
    return result

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 446ef5d2 join_the_frame")
    
