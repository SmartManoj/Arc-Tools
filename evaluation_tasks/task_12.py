from arc_tools.grid import Grid, copy_object, detect_objects, Color, SubGrid, GridRegion, GridPoint
from arc_tools.logger import logger
import math
from sympy import symbols

def eval2(expr, subs=dict()):
    try: 
        res = (expr.evalf(subs=subs))
        int_value = int(res)
        if math.isclose(res, int_value):
            return int_value
        return res
    except Exception as e:
        if not isinstance(expr, (int, float)):
            logger.error(e)
        return expr

def get_relative_positions(new_dots, obj_region):
    x1_v, y1_v, x2_v, y2_v = obj_region.x1, obj_region.y1, obj_region.x2, obj_region.y2
    mid_x = obj_region.x2 - obj_region.width//2
    mid_y = obj_region.y2 - obj_region.height//2
    result = []
    x1, x2, y1, y2 = symbols('x1 x2 y1 y2')
    subs = {x1: x1_v, x2: x2_v, y1: y1_v, y2: y2_v}
    for (rx, ry), color in new_dots:
        x = x1 if rx <= mid_x else x2
        # y = y1 if ry <= mid_y else y2
        # TODO: tricky case - if dot occurred in the middle; analyze next pattern and infer; tweak reduce mid_y
        y = y1 if ry <= mid_y - 1 else y2
        x_str = x - (eval2(x, subs) - rx)
        y_str = y - (eval2(y, subs) - ry)
        result.append(((x_str, y_str), color))
    return result

def compare_objects(obj_1, obj_2, dx, dy):
    to_be_copied_obj = obj_1.copy()
    to_be_copied_obj.replace_all_color(-1)
    grid2 = obj_2.get_full_grid()
    copied_obj = copy_object(to_be_copied_obj, dx, dy, grid2, extend_grid=True)
    combined_obj = detect_objects(grid2)[0]
    new_dots = []
    for row in range(combined_obj.height):
        for col in range(combined_obj.width):
            if combined_obj[row][col] not in [obj_1.parent_grid.background_color, -1]:
                new_color = combined_obj[row][col]
                new_dots.append(((col, row), combined_obj[row][col]))
    
    copied_obj_region_x1_y1 = GridPoint(copied_obj.region.x1 - obj_2.region.x1, copied_obj.region.y1 - obj_2.region.y1)
    copied_obj_region_x2_y2 = GridPoint(obj_2.width - 1 - (obj_2.region.x2 - copied_obj.region.x2), obj_2.height - 1 - (obj_2.region.y2 - copied_obj.region.y2))
    copied_obj_region = GridRegion([copied_obj_region_x1_y1, copied_obj_region_x2_y2])
    return get_relative_positions(new_dots, copied_obj_region), new_color

def grow_and_crop(grid: Grid) -> Grid:
    '''
    each object is growing.
    find the next objects to grow until it fits in grey L shapes.
    then crop the grid to the size of the L shapes.
    '''
    # Detect objects in the grid
    l_shapes = detect_objects(grid, required_color=Color.LIGHT_GRAY)
    cropped_region = GridRegion([
        GridPoint(l_shapes[0].region.x1, l_shapes[0].region.y1),
        GridPoint(l_shapes[1].region.x2, l_shapes[1].region.y2)
    ])

    for l_shape in l_shapes:
        grid = grid.remove_object(l_shape)

    objects = detect_objects(grid)
    # sort by size
    objects.sort(key=lambda x: x.region.width * x.region.height)

    # move object[0] to object[1]
    obj_0 = objects[0]
    obj_1 = objects[1]
    obj_2 = objects[2]
    is_vertically_arranged = obj_0.region.x2 < obj_1.region.x1
    width, height = symbols('width height')
    if is_vertically_arranged:
        # left_to_right
        is_right_to_left = obj_0.region.x1 > obj_1.region.x1
        dx = width + 1
        if is_right_to_left:
            dx = -dx
        dy = 0
    else:
        # bottom_to_top
        is_bottom_to_top = obj_0.region.y1 > obj_1.region.y1
        dx = 0
        dy = height + 1
        if is_bottom_to_top:
            dy = -dy

    subs = {width: obj_0.width, height: obj_0.height}
    dy1 = eval2(dy, subs)
    dx1 = eval2(dx, subs)
    object_color_changed = False
    second_object_color = None
    for row in range(obj_0.region.y1, obj_0.region.y2 + 1):
        for col in range(obj_0.region.x1, obj_0.region.x2 + 1):
            if grid[row][col] not in [grid[row + dy1][col + dx1], grid.background_color]:
                object_color_changed = True
                second_object_color = grid[row + dy1][col + dx1]
                break
        if object_color_changed:
            break
    new_dots_1, new_color_1 = compare_objects(obj_0, obj_1, dx1, dy1)
    subs = {width: obj_1.width, height: obj_1.height}
    dy2 = eval2(dy, subs)
    dx2 = eval2(dx, subs)
    new_dots_2, new_color_2 = compare_objects(obj_1, obj_2, dx2, dy2)
    color_sequence = [obj_0.get_max_color()]
    if second_object_color:
        color_sequence.append(second_object_color)
    for i in (new_color_1, new_color_2):
        if i not in color_sequence:
            color_sequence.append(i)
    while True:
        new_dots = [new_dots_1, new_dots_2][(len(objects) + 1) % 2]
        next_obj = objects[-1].copy()
        new_color = color_sequence[len(objects) % len(color_sequence)]
        if object_color_changed:
            obj_colors = next_obj.get_unique_values()
            if len(obj_colors) == 1:
                next_obj.replace_color(next_obj.get_max_color(), new_color)
            else:
                # new rule
                # swap colors of the objects
                next_obj.replace_color(obj_colors[0], -1)
                next_obj.replace_color(obj_colors[1], obj_colors[0])
                next_obj.replace_color(-1, obj_colors[1])


        subs = {width: next_obj.width, height: next_obj.height}
        dy = eval2(dy, subs)
        dx = eval2(dx, subs)
        next_obj = copy_object(next_obj, dx, dy, grid)

        x1, x2, y1, y2 = symbols('x1 x2 y1 y2')
        subs = {x1: next_obj.region.x1, x2: next_obj.region.x2, y1: next_obj.region.y1, y2: next_obj.region.y2}
        has_multiple_colors = len(set(color for (_, _), color in new_dots)) > 1
        
        new_points = []
        for (col, row), color in new_dots:
            new_row = eval2(row, subs)
            new_col = eval2(col, subs)
            grid[new_row][new_col] = new_color if not has_multiple_colors else color
            new_points.append(GridPoint(new_col, new_row))
        next_obj.region = GridRegion([
            GridPoint(next_obj.region.x1, next_obj.region.y1),
            GridPoint(next_obj.region.x2, next_obj.region.y2),
            GridPoint(min(p.x for p in new_points), min(p.y for p in new_points)),
            GridPoint(max(p.x for p in new_points), max(p.y for p in new_points))
        ])
        next_obj = SubGrid(next_obj.region, grid)

        cropped_grid = grid.crop(cropped_region)
        if cropped_grid.get_max_color():
            break
        objects.append(next_obj)
    return cropped_grid

if __name__ == "__main__":
    import os
    os.system("main.py 20a9e565 grow_and_crop")