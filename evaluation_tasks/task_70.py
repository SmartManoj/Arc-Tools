import os
from arc_tools.constants import CARDINAL_DIRECTIONS, EIGHT_DIRECTIONS, ORDINAL_DIRECTIONS
from arc_tools.grid import Grid, SubGrid, detect_objects, GridPoint, GridRegion
from arc_tools import logger
from arc_tools.plot import plot_grids
from collections import deque

def fill_the_tanks(grid: Grid):
    '''
    Fill enclosed areas with the paint color.
    Paint colors (appearing only once) fill areas completely enclosed by non-background colors.
    '''
    # Create a copy to work with
    result = grid.copy()
    cc = grid.get_values_count()
    paint_colors = [color for color, count in cc.items() if count == 1]
    
    # For each paint color, find objects that contain it and fill enclosed areas in those objects
    associated_pipe_colors = {}
    for paint_color in paint_colors:
        reservoir = detect_objects(result, required_color=paint_color)[0]
        # find surrounding colors
        surrounding_colors = grid.get_surrounding_values(reservoir.region.y1, reservoir.region.x1)
        associated_pipe_colors[surrounding_colors[0]] = paint_color
    for paint_color in paint_colors:
        # Find all objects that contain this paint color
        
        objects = detect_objects(result)
        for obj in objects:
            if paint_color in obj.colors:
                # Find enclosed areas within this object's region in the main grid
                # plot_grids([obj])
                enclosed_areas = find_enclosed_areas(obj, associated_pipe_colors)
                for area in enclosed_areas:
                    is_valid, surrounding_colors = is_valid_area(area, obj)
                    if is_valid:
                        # filter pipe color from surrounding colors
                        pipe_color = [color for color in surrounding_colors if color in associated_pipe_colors][0]
                        paint_color = associated_pipe_colors[pipe_color]
                        fill_area_directly(result, obj, area, paint_color)
    
    return result

def is_valid_area(area: list[GridPoint], obj: SubGrid):
    """
    Check if the area is valid by examining surrounding colors.
    The area is valid if it's actually surrounded by walls (non-background colors).
    """
    if not area:
        return False
    
    # Get unique colors in the immediate surrounding of the area
    surrounding_colors = set()
    region_points = set()
    for row, col in area:
        for dr, dc in CARDINAL_DIRECTIONS:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < obj.height and 0 <= new_col < obj.width:
                region_points.add((new_row, new_col))
    for row, col in region_points:
        # Check immediate neighbors
        for dc, dr in EIGHT_DIRECTIONS:
            new_row, new_col = row + dr, col + dc
            if (0 <= new_row < obj.height and 
                0 <= new_col < obj.width):
                color = obj[new_row][new_col]
                if color != obj.background_color:
                    surrounding_colors.add(color)

    # Valid if at least one non-background color found in surrounding
    # plot_grids([grid])
    return len(surrounding_colors) >= 2, surrounding_colors

def find_enclosed_areas(obj: SubGrid, associated_pipe_colors: dict):
    """
    Find enclosed areas within a specific region of the grid.
    """
    enclosed_areas = []
    visited = set()
    
    for row in range(obj.height):
        for col in range(obj.width):
            if (row, col) not in visited and obj[row][col] == obj.background_color:
                # Use flood fill to find connected background region
                region_points = []
                queue = deque([(row, col)])
                visited.add((row, col))
                touches_region_edge = False
                
                while queue:
                    curr_row, curr_col = queue.popleft()
                    region_points.append((curr_row, curr_col))
                    
                    # Check if this point touches the SubGrid edge (relative coordinates)
                    if (curr_row == 0 or curr_row == obj.height - 1 or 
                        curr_col == 0 or curr_col == obj.width - 1):
                        touches_region_edge = True
                    
                    # Check 4-connected neighbors
                    for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                        new_row, new_col = curr_row + dr, curr_col + dc
                        
                        if (0 <= new_row < obj.height and 
                            0 <= new_col < obj.width and 
                            (new_row, new_col) not in visited and
                            obj[new_row][new_col] == obj.background_color):
                            visited.add((new_row, new_col))
                            queue.append((new_row, new_col))
                
                # if all boundary points are same, then it is not enclosed
                boundary_points = set()
                is_enclosed = True
                for row, col in region_points:
                    for dr, dc in CARDINAL_DIRECTIONS:
                        new_row, new_col = row + dr, col + dc
                        value = obj[new_row][new_col]
                        if 0 <= new_row < obj.height and 0 <= new_col < obj.width and value in associated_pipe_colors:
                            is_enclosed = False
                            break
                    if not is_enclosed:
                        break
                
                if is_enclosed:
                    enclosed_areas.append(region_points)
    return enclosed_areas

def fill_area_directly(grid: Grid, obj: SubGrid, points: list, fill_color: int):
    """
    Fill the specified points in the grid with the given fill color.
    Points are already in absolute grid coordinates.
    """
    for row, col in points:
        if 0 <= row < grid.height and 0 <= col < grid.width:
            grid[row + obj.region.y1][col + obj.region.x1] = fill_color

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 8b7bacbf fill_the_tanks") 
