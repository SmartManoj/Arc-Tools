from collections import Counter
from arc_tools import grid
from arc_tools.grid import Grid, detect_objects, Color, SubGrid, GridRegion, GridPoint
from arc_tools.plot import plot_grid, plot_grids
from itertools import combinations
from arc_tools.logger import logger
from copy import deepcopy

def is_l_shape(obj: SubGrid) -> bool:
    """
    Check if an object is L-shaped.
    An L-shape has exactly 3 cells in a corner formation.
    """
    if obj.get_total_dots() != 3:
        return False
    
    # Get all non-background cells
    cells = []
    for y in range(obj.region.y1, obj.region.y2 + 1):
        for x in range(obj.region.x1, obj.region.x2 + 1):
            if obj.parent_grid[y][x] != obj.background_color:
                cells.append((x, y))
    
    if len(cells) != 3:
        return False
    
    # Check if cells form an L shape
    # Sort cells by x and y
    cells.sort()
    x1, y1 = cells[0]
    x2, y2 = cells[1]
    x3, y3 = cells[2]
    # Check for horizontal L
    if x1 == x2 and y2 == y3 and y3 == y1 + 1:
        return True
    # Check for vertical L (rotated 90 degrees)
    if x1 == x2 and y1 == y3 and y2 == y3 + 1:
        return True
    # Check for mirrored L shapes (rotated 180 degrees)
    if x2 == x3 and y1 == y2 and y3 == y2 + 1:
        return True
    # Check for mirrored L shapes (rotated 270 degrees)
    if x2 == x3 and y1 == y3 and y1 == y2 + 1:
        return True
    return False

def get_corner_direction(obj: SubGrid) -> tuple:
    """
    Get the direction of the corner of an L-shaped object.
    Returns (dx, dy) where dx and dy are -1, 0, or 1
    """
    cells = []
    for y in range(obj.region.y1, obj.region.y2 + 1):
        for x in range(obj.region.x1, obj.region.x2 + 1):
            if obj.parent_grid[y][x] != obj.background_color:
                cells.append((x, y))
    
    cells.sort()
    x1, y1 = cells[0]
    x2, y2 = cells[1]
    x3, y3 = cells[2]
    
    # Check for horizontal L
    if x1 == x2 and y2 == y3 and y3 == y1 + 1:
        return (-1, 1)
    # Check for vertical L (rotated 90 degrees)
    if x1 == x2 and y1 == y3 and y2 == y3 + 1:
        return (-1, -1)
    # Check for mirrored L shapes (rotated 180 degrees)
    if x2 == x3 and y1 == y2 and y3 == y2 + 1:
        return (1, -1)
    # Check for mirrored L shapes (rotated 270 degrees)
    if x2 == x3 and y1 == y3 and y1 == y2 + 1:
        return (1, 1)

def shoot_light(grid: Grid) -> Grid:
    '''
    L-shaped guns shoot light in the corner direction of the L.
    Once it touches an object, the color of the light is changed to the color of the object and reflected.
    '''
    result = grid.copy()
    objects = detect_objects(result, single_color_only=True, go_diagonal=False)
    # Find all L-shaped objects
    l_shapes = [obj for obj in objects if is_l_shape(obj)]
    
    for l_shape in l_shapes:
        # Get the corner direction
        dx, dy = get_corner_direction(l_shape)
        # Start from the corner of the L
        corner_x = l_shape.region.x2 if dx > 0 else l_shape.region.x1
        corner_y = l_shape.region.y2 if dy > 0 else l_shape.region.y1
        
        # Shoot light until it touches an object or goes out of bounds
        x, y = corner_x + dx, corner_y + dy
        light_color = result[corner_y][corner_x]
        # TODO: remove count
        count = 0
        while 0 <= x < len(result[0]) and 0 <= y < len(result) and count < 100:
            # bottom
            if y+1 < len(result) and grid[y+1][x] != result.background_color and dy > 0:
                light_color = grid[y+1][x]
                dx, dy = dx, -dy
            # right
            elif x+1 < len(result[0]) and grid[y][x + 1] != result.background_color and dx > 0:
                light_color = grid[y][x+1]
                dx, dy = -dx, dy
            # top
            elif y-1 >= 0 and grid[y-1][x] != result.background_color and dy < 0:
                light_color = grid[y-1][x]
                dx, dy = dx, -dy
            # left
            elif x-1 >= 0 and grid[y][x-1] != result.background_color and dx < 0:
                light_color = grid[y][x-1]
                dx, dy = -dx, dy
            result[y][x] = light_color
            x += dx
            y += dy
            count +=1
    
    return result

if __name__ == "__main__":
    import os
    os.system("main.py 142ca369 shoot_light")