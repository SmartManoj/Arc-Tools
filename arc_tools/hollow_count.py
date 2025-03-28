from collections import deque, defaultdict
import json
from arc_tools.extract_knowledge import extract_knowledge
from copy import deepcopy
from arc_tools.grid import Grid
def count_hollows_per_number(grid):
    grid = deepcopy(grid)
    grid = extract_knowledge(grid)
    rows, cols = len(grid), len(grid[0])
    visited = [[False]*cols for _ in range(rows)]
    directions = [(-1,0), (1,0), (0,-1), (0,1), (-1,-1), (-1,1), (1,-1), (1,1)]
    hollow_count = defaultdict(int)

    def is_border(r, c):
        return r == 0 or r == rows - 1 or c == 0 or c == cols - 1

    def bfs_zero(r, c):
        queue = deque()
        queue.append((r, c))
        visited[r][c] = True
        is_connected_to_border = is_border(r, c)
        region = [(r, c)]
        border_values = set()

        while queue:
            x, y = queue.popleft()
            for dx, dy in directions:
                nx, ny = x+dx, y+dy
                if 0 <= nx < rows and 0 <= ny < cols:
                    if grid[nx][ny] == 0 and not visited[nx][ny]:
                        visited[nx][ny] = True
                        queue.append((nx, ny))
                        region.append((nx, ny))
                        if is_border(nx, ny):
                            is_connected_to_border = True
                    elif grid[nx][ny] != 0:
                        border_values.add(grid[nx][ny])

        # hollow must be fully enclosed and surrounded by only 1 unique value
        if not is_connected_to_border and len(border_values) == 1:
            hollow_count[list(border_values)[0]] += 1

    for i in range(rows):
        for j in range(cols):
            if grid[i][j] == 0 and not visited[i][j]:
                bfs_zero(i, j)

    numbers = dict.fromkeys(cell for row in grid for cell in row if cell != 0)
    hollow_count_dict = {}
    for num in numbers:
        hollow_count_dict[hollow_count.get(num, 0)] = num
    return hollow_count_dict

def count_hollows_task(grid_o: Grid) -> Grid:
    grid = grid_o.grid
    rows = len(grid)
    cols = len(grid[0])
    visited = [[False]*cols for _ in range(rows)]
    object_mask = [[-1]*cols for _ in range(rows)]

    dirs8 = [(-1, -1), (-1, 0), (-1, 1),
            ( 0, -1),          ( 0, 1),
            ( 1, -1), ( 1, 0), ( 1, 1)]

    dirs4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def flood_fill_object(r, c, obj_id):
        stack = [(r, c)]
        object_cells = []

        while stack:
            x, y = stack.pop()
            if visited[x][y]:
                continue
            visited[x][y] = True
            object_mask[x][y] = obj_id
            object_cells.append((x, y))
            for dx, dy in dirs8:
                nx, ny = x + dx, y + dy
                if 0 <= nx < rows and 0 <= ny < cols:
                    if not visited[nx][ny] and grid[nx][ny] == 5:
                        stack.append((nx, ny))
        return object_cells

    def count_hollows(obj_cells):
        # Create subgrid bounds
        min_r = min(x for x, y in obj_cells) - 1
        max_r = max(x for x, y in obj_cells) + 1
        min_c = min(y for x, y in obj_cells) - 1
        max_c = max(y for x, y in obj_cells) + 1

        sub_rows = max_r - min_r + 1
        sub_cols = max_c - min_c + 1

        subgrid = [[0]*sub_cols for _ in range(sub_rows)]
        subvisited = [[False]*sub_cols for _ in range(sub_rows)]

        for x, y in obj_cells:
            subgrid[x - min_r][y - min_c] = 1  # Mark object

        def is_hollow(r, c):
            stack = [(r, c)]
            hollow = True
            while stack:
                x, y = stack.pop()
                if subvisited[x][y]:
                    continue
                subvisited[x][y] = True
                if x == 0 or y == 0 or x == sub_rows-1 or y == sub_cols-1:
                    hollow = False
                for dx, dy in dirs4:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < sub_rows and 0 <= ny < sub_cols:
                        if not subvisited[nx][ny] and subgrid[nx][ny] == 0:
                            stack.append((nx, ny))
            return hollow

        hollows = 0
        for r in range(sub_rows):
            for c in range(sub_cols):
                if subgrid[r][c] == 0 and not subvisited[r][c]:
                    if is_hollow(r, c):
                        hollows += 1
        return hollows

    # Step 1: Identify objects
    object_id = 0
    object_cells_dict = {}
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 5 and not visited[r][c]:
                cells = flood_fill_object(r, c, object_id)
                object_cells_dict[object_id] = cells
                object_id += 1

    hollow_count_dict = count_hollows_per_number(grid)

    # Step 2: Count hollows in each object and replace values
    for oid, cells in object_cells_dict.items():
        hollow_count = count_hollows(cells)
        for x, y in cells:
            grid[x][y] = hollow_count_dict.get(hollow_count, 0)

    return Grid(grid)
if __name__ == "__main__":
    # Load and slice input grid
    file = open('C:/Users/smart/Desktop/GD/ARC-AGI-2/data/evaluation/e3721c99.json', 'r')
    data = json.load(file)
    grid = (data['train'][0]['input'])[:5]


    hollow_count_dict = count_hollows_per_number(grid)

    from pprint import pprint
    pprint(hollow_count_dict)
