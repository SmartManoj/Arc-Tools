import os
from collections import deque
from arc_tools.grid import Grid, detect_objects, Color, GridPoint
from arc_tools import logger
from arc_tools.plot import plot_grids


def attract(grid: Grid):
    '''
    maroon dots are moved to green box
    '''
    def distance_to_start(point):
        # find the distance from point to green object using pathfinding through orange areas
        # Use BFS to find shortest path through orange areas (navigable)
        start = (point.y, point.x)
        
        # BFS queue: (row, col, path_length)
        queue = deque([(start[0], start[1], 0)])
        visited = {start}
        
        # Directions: up, down, left, right (cardinal directions only)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        while queue:
            row, col, path_length = queue.popleft()
            
            # Check if we've reached any point in the green object
            for green_point in green_obj.points:
                if (row, col) == (green_point.y, green_point.x):
                    return path_length
            
            for dr, dc in directions:
                new_row, new_col = row + dr, col + dc
                
                # Check bounds and if not visited
                if (0 <= new_row < grid.height and 
                    0 <= new_col < grid.width and
                    (new_row, new_col) not in visited):
                    
                    cell_color = grid[new_row][new_col]
                    # Allow movement through orange areas, maroon dots, and green areas
                    if cell_color == Color.ORANGE.value or cell_color == Color.MAROON.value or cell_color == Color.GREEN.value or cell_color == Color.RED.value:
                        visited.add((new_row, new_col))
                        queue.append((new_row, new_col, path_length + 1))
        
        # If no path found, return a large number
        return float('inf')
        
        
    obc = Color.ORANGE.value
    grid.background_color = Color.MAGENTA.value
    objects = detect_objects(grid)
    for obj in objects:
        if Color.GREEN.value in obj.colors:
            main_obj = obj
            break
    
    v = min(9, main_obj.get_values_count()[Color.MAROON.value])
    green_obj = detect_objects(grid, required_colors=[Color.GREEN.value, Color.RED.value])[0]
    green_obj.points.sort(key=lambda x: x.y)
    maroon_points = [point for point in main_obj.points if grid[point.y][point.x] == Color.MAROON.value]
    # sort by nearest to main_obj.region.start
    maroon_points.sort(key=lambda x: distance_to_start(x))
    for point in maroon_points[:v]:
        grid[point.y][point.x] = obc
    for point in green_obj.points[:v]:
        grid[point.y][point.x] = Color.MAROON.value

    return grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py dd6b8c4b attract") 
