from json import detect_encoding
import os
from collections import Counter

from arc_tools.grid import BorderSide, Grid, detect_objects
from arc_tools.logger import logger
from arc_tools.plot import plot_grid, plot_grids

def light_rays(grid: Grid) -> Grid:
    '''
    Expand light from source into the cave; 
    outside the cave, it will based on the cave open side shape.
    '''
    cave_color = grid.get_max_color()
    objects = detect_objects(grid)
    # plot_grids(objects)
    # cave having obj with cave_color
    obstacles = []
    for obj in objects:
        if cave_color in obj.colors:
            cave = obj
        else:
            obstacles.append(obj)
    light_source = detect_objects(cave, ignore_colors=[cave_color])[0]

    
    # Use flood fill to expand from light source
    expand_light(grid, cave, light_source, light_source.color, cave_color)
    for side in BorderSide:
        if any(p.value==light_source.color for p in cave.get_edge_points(side)):
            cave_open_side = side
            break
    # plot_grids([cave, grid])
    if cave_open_side == BorderSide.TOP:
        # check how many rows are equal
        row_1_capacity = sum(grid[cave.region.y1][col] in [grid.background_color, cave_color] for col in range(cave.region.x1, cave.region.x2))
        depth = 1
        for i in range(1, cave.height):
            row_i_capacity = sum(grid[cave.region.y1 + i][col] in [grid.background_color, cave_color] for col in range(cave.region.x1, cave.region.x2))
            if row_i_capacity != row_1_capacity:
                break
            depth += 1

        for i, row in enumerate(reversed(range(cave.region.y1))):
            k = i // depth
            for col in range(cave.region.x1 - k, cave.region.x2+1+k):
                if grid[row][col] in [grid.background_color, cave_color]:
                    grid[row][col] = light_source.color

        for obstacle in obstacles:
            for row in reversed(range(obstacle.region.y1)):
                break_inner = False
                for col in range(obstacle.region.x1, obstacle.region.x2+1):
                    if grid[row][col] == light_source.color:
                        grid[row][col] = grid.background_color
                    else:
                        break_inner = True
                        break
                if break_inner:
                        break
    elif cave_open_side == BorderSide.LEFT:
        # check how many columns are equal
        
        col_1_capacity = sum(grid[row][cave.region.x1] in [grid.background_color, cave_color] for row in range(cave.region.y1, cave.region.y2))
        width = 1
        for i in range(1, cave.width):
            col_i_capacity = sum(grid[row][cave.region.x1 + i] in [grid.background_color, cave_color] for row in range(cave.region.y1, cave.region.y2))
            if col_i_capacity != col_1_capacity:
                break
            width += 1
        for i, col in enumerate(reversed(range(cave.region.x1))):
            k = i // width
            for row in range(cave.region.y1 - k, cave.region.y2+1+k):
                if grid[row][col] in [grid.background_color, cave_color]:
                    grid[row][col] = light_source.color
        for obstacle in obstacles:
            for col in reversed(range(obstacle.region.x1)):
                break_inner = False
                for row in range(obstacle.region.y1, obstacle.region.y2+1):
                    if grid[row][col] == light_source.color:
                        grid[row][col] = grid.background_color
                    else:
                        break_inner = True
                        break
                if break_inner:
                        break

    elif cave_open_side == BorderSide.BOTTOM:
        # check how many rows are equal
        row_1_capacity = sum(grid[cave.region.y2][col] in [grid.background_color, cave_color] for col in range(cave.region.x1, cave.region.x2))
        depth = 1
        for i in range(1, cave.height):
            row_i_capacity = sum(grid[cave.region.y2 + i][col] in [grid.background_color, cave_color] for col in range(cave.region.x1, cave.region.x2))
            if row_i_capacity != row_1_capacity:
                break
            depth += 1
        # in last row, find where cave is started and end
        for col in range(cave.region.x1, cave.region.x2+1):
            if grid[cave.region.y2][col] == cave_color:
                cave_start = col
                break
        for col in range(cave.region.x2, cave.region.x1-1, -1):
            if grid[cave.region.y2][col] == cave_color:
                cave_end = col
                break
        for i, row in enumerate(range(cave.region.y2 + 1, grid.height)):
            k = i // depth
            for col in range(cave_start - k, cave_end+1+k):
                if grid[row][col] in [grid.background_color, cave_color]:
                    grid[row][col] = light_source.color
        for obstacle in obstacles:
            for row in range(obstacle.region.y2 + 1, grid.height):
                break_inner = False
                for col in range(obstacle.region.x1, obstacle.region.x2+1):
                    if grid[row][col] == light_source.color:
                        grid[row][col] = grid.background_color
                    else:
                        break_inner = True
                        break
                if break_inner:
                        break
    elif cave_open_side == BorderSide.RIGHT:
        # check how many columns are equal
        col_1_capacity = sum(grid[row][cave.region.x2] in [grid.background_color, cave_color] for row in range(cave.region.y1, cave.region.y2))
        width = 1
        for i in range(1, cave.width):
            col_i_capacity = sum(grid[row][cave.region.x2 + i] in [grid.background_color, cave_color] for row in range(cave.region.y1, cave.region.y2))
            if col_i_capacity != col_1_capacity:
                break
            width += 1
        for i, col in enumerate(range(cave.region.x2 + 1, grid.width)):
            k = i // width
            for row in range(cave.region.y1 - k, cave.region.y2+1+k):
                if grid[row][col] in [grid.background_color, cave_color]:
                    grid[row][col] = light_source.color
        for obstacle in obstacles:
            for col in range(obstacle.region.x2 + 1, grid.width):
                break_inner = False
                for row in range(obstacle.region.y1, obstacle.region.y2+1):
                    if grid[row][col] == light_source.color:
                        grid[row][col] = grid.background_color
                    else:
                        break_inner = True
                        break
                if break_inner:
                        break
    return grid

def expand_light(grid: Grid, cave: Grid, light_source: Grid, light_color: int, cave_color: int):
    '''
    Expand light from source region to fill the cave using flood fill
    '''
    
    # Get all positions in the light source
    light_positions = []
    for row in range(light_source.height):
        for col in range(light_source.width):
            if light_source[row][col] == light_color:
                # Convert to global coordinates using the region
                global_row = row + light_source.region.y1
                global_col = col + light_source.region.x1
                light_positions.append((global_row, global_col))
    
    
    visited = set()
    queue = list(light_positions)
    
    while queue:
        row, col = queue.pop(0)
        
        if (row, col) in visited:
            continue
            
        visited.add((row, col))
        
        # Check if this position is within the cave and not a wall
        # Convert to cave coordinates
        cave_row = row - cave.region.y1
        cave_col = col - cave.region.x1
        
        if (0 <= cave_row < cave.height and 0 <= cave_col < cave.width and 
            cave[cave_row][cave_col] != cave_color and grid[row][col] in [light_color, grid.background_color] ):
            grid[row][col] = light_color
            cave[cave_row][cave_col] = light_color
            
            # Add neighboring positions to queue
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                new_row, new_col = row + dr, col + dc
                if (new_row, new_col) not in visited:
                    # Check if the neighbor is within the cave
                    new_cave_row = new_row - cave.region.y1
                    new_cave_col = new_col - cave.region.x1
                    if (0 <= new_cave_row < cave.height and 0 <= new_cave_col < cave.width and 
                        cave[new_cave_row][new_cave_col] != cave_color):
                        queue.append((new_row, new_col))

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py b9e38dc0 light_rays") 
