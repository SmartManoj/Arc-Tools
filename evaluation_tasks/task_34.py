import os
from arc_tools.grid import Color, Grid, detect_objects, GridPoint

def shoot_the_center(grid: Grid):
    """
    Transforms a grid based on a central crosshair defined by marker dots.

    1. Identify Components:
        - The "main object" is identified (typically orange).
        - "Marker dots" are identified as any non-background, non-main-object-color points located on the grid's borders.
    2. Define Center:
        - A central crosshair is defined. The vertical line's x-coordinate (cx) is determined by the top or bottom marker dots.
        - The horizontal line's y-coordinate (cy) is determined by the left or right marker dots.
    3. Transform Quadrants:
        - The main object is divided into four quadrants by the crosshair.
        - Depending on which marker dots are present (top, bottom, left, right), the corresponding quadrants of the main object are moved to the corners of a new, empty grid.
    4. Preserve Crosshair:
        - The parts of the original main object that lie on the vertical (x=cx) or horizontal (y=cy) lines of the crosshair are copied to their original positions in the new grid.
    5. Draw Guide Lines:
        - Red lines are drawn on the crosshair in the new grid, extending from the center towards the active marker directions, but only on empty cells.
    """
    
    objects = detect_objects(grid)
    if not objects:
        return grid

    # Find marker dots (non-background, non-orange)
    marker_dots = [GridPoint(c, r) for r in range(grid.height) for c in range(grid.width) if grid[r][c] not in [grid.background_color, Color.ORANGE.value]]

    orange_objects = [obj for obj in objects if obj.color == Color.ORANGE.value]
    if not orange_objects:
        return grid
    main_color = Color.ORANGE.value
    main_object_points = [p for obj in orange_objects for p in obj.points]

    # The center is the intersection of the vertical line from the top dot
    # and the horizontal line from the right dot.
    # find y is 0,
    top_dot = next((p for p in marker_dots if p.y == 0), None)
    right_dot = next((p for p in marker_dots if p.x == grid.width - 1), None)
    left_dot = next((p for p in marker_dots if p.x == 0), None)
    bottom_dot = next((p for p in marker_dots if p.y == grid.height - 1), None)
    
    cx = top_dot.x if top_dot else bottom_dot.x if bottom_dot else -1
    cy = right_dot.y if right_dot else left_dot.y if left_dot else grid.height if top_dot else -1

    new_grid = Grid([[grid.background_color] * grid.width for _ in range(grid.height)], background_color=grid.background_color)

    # Determine which quadrants are active based on marker positions
    has_top_marker = any(p.y < cy for p in marker_dots)
    has_bottom_marker = any(p.y > cy for p in marker_dots)
    has_left_marker = any(p.x < cx for p in marker_dots)
    has_right_marker = any(p.x > cx for p in marker_dots)
    
    quadrants = {
        'tl': (lambda p: p.x < cx and p.y < cy, has_left_marker or has_top_marker),
        'tr': (lambda p: p.x > cx and p.y < cy, has_right_marker or has_top_marker),
        'bl': (lambda p: p.x < cx and p.y > cy, has_left_marker or has_bottom_marker),
        'br': (lambda p: p.x > cx and p.y > cy, has_right_marker or has_bottom_marker),
    }

    # 1. Move quadrant pieces to the corners if they contain any object points
    moved_points = set()
    for q_name, (q_func, is_active) in quadrants.items():
        if not is_active:
            continue
        q_points = [p for p in main_object_points if q_func(p)]
        if not q_points:
            continue
        
        min_x = min(p.x for p in q_points)
        max_x = max(p.x for p in q_points)
        min_y = min(p.y for p in q_points)
        max_y = max(p.y for p in q_points)

        q_width = max_x - min_x + 1
        q_height = max_y - min_y + 1

        if q_name == 'tl':
            target_x, target_y = 0, 0
        elif q_name == 'tr':
            target_x, target_y = grid.width - q_width, 0
        elif q_name == 'bl':
            target_x, target_y = 0, grid.height - q_height
        elif q_name == 'br':
            target_x, target_y = grid.width - q_width, grid.height - q_height

        for p in q_points:
            rel_x = p.x - min_x
            rel_y = p.y - min_y
            new_grid[target_y + rel_y][target_x + rel_x] = main_color
            moved_points.add(p)

    # 2. Preserve stationary parts of the original object that lie on the crosshair
    for p in main_object_points:
        if p.x == cx or p.y == cy:
            new_grid[p.y][p.x] = main_color

        # Draw lines: up from (cx, cy) and right from (cx, cy)
    main_object = [obj for obj in objects if obj.color == Color.ORANGE.value][0]
    vertical_range = range(main_object.region.y2+1) if has_top_marker else reversed(range(main_object.region.y1, grid.height))
    horizontal_range = range(main_object.region.x1, grid.width) if has_right_marker else reversed(range(main_object.region.x2, grid.width))
    for y in vertical_range:
        if new_grid[y][cx] == grid.background_color:
            new_grid[y][cx] = Color.RED.value
    for x in horizontal_range:
        if new_grid[cy][x] == grid.background_color:
            new_grid[cy][x] = Color.RED.value
    # remove excess red pixels
    vertical_range = range(main_object.region.y2, cy, -1) if has_top_marker else range(main_object.region.y1, grid.height)
    horizontal_range = range(main_object.region.x1, cx) if has_right_marker else range(main_object.region.x2, grid.width)
    for y in vertical_range:
        if new_grid[y][cx] != Color.RED.value:
            break
        new_grid[y][cx] = grid.background_color
    for x in horizontal_range:
        if new_grid[cy][x] != Color.RED.value:
            break
        new_grid[cy][x] = grid.background_color
            
    

    return new_grid


if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 4a21e3da shoot_the_center")
