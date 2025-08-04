from typing import List, Tuple, Optional
from collections import deque

from .grid import Grid, SubGrid


def scale_to_9x9(grid: Grid):
    """Scale grid to 9x9 by factor"""
    grid_size = len(grid)
    new_size = 9
    result = [[0 for _ in range(new_size)] for _ in range(new_size)]
    factor = grid_size / new_size
    
    for i in range(new_size):
        for j in range(new_size):
            # Map 9x9 position to 6x6 position
            src_i = int(i * factor)
            src_j = int(j * factor)
            
            # Take the value from the source position
            result[i][j] = grid[src_i][src_j]
    result = Grid(result, grid.background_color)
    if type(grid) != Grid:
        result = result.as_sub_grid()
    return result

def path_to_moves(path: List[Tuple[int, int]]) -> List[str]:
    moves = []
    for i in range(1, len(path)):
        prev_row, prev_col = path[i-1]
        curr_row, curr_col = path[i]
        
        if curr_row < prev_row:
            moves.append("move_up")
        elif curr_row > prev_row:
            moves.append("move_down")
        elif curr_col < prev_col:
            moves.append("move_left")
        elif curr_col > prev_col:
            moves.append("move_right")
    return moves

def find_path(grid: Grid, start_obj: SubGrid, end_obj: SubGrid, scale_factor: int) -> List[str]:
    """
    Find path from S to E in the grid using BFS.
    Returns list of coordinates (row, col) representing the path.
    """
    zone_size = 8 // scale_factor
    start_pos = start_obj.region.x1 // zone_size, start_obj.region.y1 // zone_size
    end_pos = end_obj.region.x1 // zone_size * zone_size / zone_size, end_obj.region.y1 // zone_size * zone_size / zone_size
    grid = compress_grid(grid, start_pos, end_pos, scale_factor)
    # print(start_pos, end_pos)
    # for row in grid:
    #     print(''.join(row))
    rows = len(grid)
    cols = len(grid[0])
    
    # Find start (S) and end (E) positions
    start = None
    end = None
    
    for row in range(rows):
        for col in range(cols):
            if grid[row][col] == 'S':
                start = (row, col)
            elif grid[row][col] == 'E':
                end = (row, col)
    
    if not start or not end:
        return []
    
    # BFS to find shortest path
    queue = deque([(start, [start])])
    visited = {start}
    
    # Directions: up, down, left, right
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    while queue:
        (row, col), path = queue.popleft()
        
        if (row, col) == end:
            return path_to_moves(path)
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            
            # Check bounds
            if (0 <= new_row < rows and 
                0 <= new_col < cols and
                (new_row, new_col) not in visited and
                grid[new_row][new_col] != 'X'):
                
                visited.add((new_row, new_col))
                new_path = path + [(new_row, new_col)]
                queue.append(((new_row, new_col), new_path))
    
    return []

def compress_grid(grid: Grid, start_pos: Tuple[int, int], end_pos: Tuple[int, int], scale_factor: int):
    """function to visualize grid"""
    compressed_grid = []
    # zone 8*8 ; grid 64*64
    #  now print zone row 5 only
    zone_size = 8 // scale_factor
    zone_row_idx_start = 0
    zone_row_idx_end = len(grid) // zone_size - 1


    for zone_row_idx, zone_row in enumerate(grid[zone_row_idx_start*zone_size:(zone_row_idx_end+1)*zone_size:zone_size], start=zone_row_idx_start):
        row = []
        for zone_col_idx, zone_col in enumerate(zone_row[::zone_size]):
            if (zone_col_idx, zone_row_idx) == start_pos:
                row.append('S')
            elif (zone_col_idx, zone_row_idx) == end_pos:
                row.append('E')
            elif zone_col == grid.background_color:
                row.append('X')
            else:
                row.append('-')
        compressed_grid.append(row)
    
    return compressed_grid
