from collections import Counter, deque
from enum import Enum
import numpy as np
import logging
import copy
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MyEnum(Enum):
    def __repr__(self):
        return f"{self.__class__.__name__}.{self.name}"

class ColorCodes(MyEnum):
    BLACK = 0
    BLUE = 1
    RED = 2
    GREEN = 3
    YELLOW = 4
    GRAY = 5
    PURPLE = 6
    ORANGE = 7
    LIGHTBLUE = 8
    BROWN = 9

class BorderSide(MyEnum):
    LEFT = 0
    RIGHT = 1
    TOP = 2
    BOTTOM = 3

class GridPoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __str__(self):
        return f"({self.x}, {self.y})"
    
    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

class GridRegion:
    def __init__(self, points: list[GridPoint]):
        self.x1 = min(p.x for p in points)
        self.x2 = max(p.x for p in points)
        self.y1 = min(p.y for p in points)
        self.y2 = max(p.y for p in points)

    def __str__(self):
        return f"[(x1/y1)=({self.x1}/{self.y1}), (x2/y2)=({self.x2}/{self.y2})]"

class GridObject:
    def __init__(self, region: GridRegion, parent_grid: list[list[int]]):
        self.region = region # Keep the attribute name 'region' for consistency
        self.parent_grid = parent_grid
        self.grid = self.get_subgrid()

    def __str__(self):
        return f"Region: {self.region}"
    
    def get_values_count(self):
        values = Counter()
        for i in self.grid:
            for j in i:
                value = j
                if value != 0:
                    values[value] += 1
        return values
    
    def get_min_value(self):
        min_key, _ = min(self.get_values_count().items(), key=lambda x: x[1])
        return min_key
    
    def get_max_value(self):
        max_key, _ = max(self.get_values_count().items(), key=lambda x: x[1])
        return max_key
    
    def get_border_sides(self, point: GridPoint):
        sides = []
        if point.x == self.region.x1:
            sides.append(BorderSide.LEFT)
        if point.x == self.region.x2:
            sides.append(BorderSide.RIGHT)
        if point.y == self.region.y1:
            sides.append(BorderSide.TOP)
        if point.y == self.region.y2:
            sides.append(BorderSide.BOTTOM)
        return sides
    
    def get_points_of_dots(self, value):
        positions = []
        for i in range(self.region.x1, self.region.x2 + 1):
            for j in range(self.region.y1, self.region.y2 + 1):
                if self.parent_grid[j][i] == value:
                    positions.append(GridPoint(i, j))
        return positions
    
    def get_points_and_sides_of_dots(self, value):
        points = self.get_points_of_dots(value)
        points_and_sides = []
        for point in points:
            points_and_sides.append((point, self.get_border_sides(point)))
        return points_and_sides
    
    def get_subgrid(self):
        grid = [[0 for _ in range(self.region.x2 - self.region.x1 + 1)] for _ in range(self.region.y2 - self.region.y1 + 1)]
        for i in range(self.region.x1, self.region.x2 + 1):
            for j in range(self.region.y1, self.region.y2 + 1):
                grid[j - self.region.y1][i - self.region.x1] = self.parent_grid[j][i]
        return grid
    
    def get_full_grid(self):
        n_parent_rows, n_parent_cols = len(self.parent_grid), len(self.parent_grid[0])
        grid = [[0 for _ in range(n_parent_cols)] for _ in range(n_parent_rows)]
        for i in range(self.region.x1, self.region.x2 + 1):
            for j in range(self.region.y1, self.region.y2 + 1):
                grid[j][i] = self.parent_grid[j][i]
        return grid
    
    def has_yellow_block(self):
        return ColorCodes.YELLOW.value in self.get_unique_values()
    
    def get_unique_values(self):
        return list(self.get_values_count().keys())

    def has_hollow_space(self):
        """
        Checks if a grid contains a 'hollow space' - a region of 0s
        completely surrounded by non-zero values.
        Uses BFS starting from border 0s to find all externally connected 0s.
        Any remaining 0s are considered internal/hollow.
        """
        if not self.grid or not self.grid[0]:
            return False # Handle empty or invalid grid

        rows, cols = len(self.grid), len(self.grid[0])
        visited = [[False for _ in range(cols)] for _ in range(rows)]
        q = deque()

        # Add border 0s to the queue and mark as visited
        for r in range(rows):
            # Left border
            if self.grid[r][0] == 0 and not visited[r][0]:
                q.append((r, 0))
                visited[r][0] = True
            # Right border
            if self.grid[r][cols - 1] == 0 and not visited[r][cols - 1]:
                q.append((r, cols - 1))
                visited[r][cols - 1] = True

        for c in range(cols): # Avoid double-adding corners
            # Top border
            if self.grid[0][c] == 0 and not visited[0][c]:
                q.append((0, c))
                visited[0][c] = True
            # Bottom border
            if self.grid[rows - 1][c] == 0 and not visited[rows - 1][c]:
                q.append((rows - 1, c))
                visited[rows - 1][c] = True

        while q:
            r, c = q.popleft()
            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and \
                self.grid[nr][nc] == 0 and not visited[nr][nc]:
                    visited[nr][nc] = True
                    q.append((nr, nc))

        for r in range(rows):
            for c in range(cols):
                if self.grid[r][c] == 0 and not visited[r][c]:
                    return True

        return False 

def detect_objects(grid) -> list[GridObject]:
    grid_np = np.array(grid)
    rows, cols = grid_np.shape
    visited = np.zeros_like(grid_np, dtype=bool)
    objects = []

    for r in range(rows):
        for c in range(cols):
            if grid_np[r, c] != 0 and not visited[r, c]:
                # Start BFS for a new object
                current_object_points = []
                q = deque([(r, c)])
                visited[r, c] = True

                while q:
                    row, col = q.popleft()
                    current_object_points.append(GridPoint(col, row)) # x=col, y=row

                    # Check neighbors (4-connectivity: up, down, left, right)
                    for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                        nr, nc = row + dr, col + dc
                        if 0 <= nr < rows and 0 <= nc < cols and \
                           grid_np[nr, nc] != 0 and not visited[nr, nc]:
                            visited[nr, nc] = True
                            q.append((nr, nc))
                
                # filter only the corner points
                current_object_points = [p for p in current_object_points if p.x == min(p.x for p in current_object_points) or p.x == max(p.x for p in current_object_points) or p.y == min(p.y for p in current_object_points) or p.y == max(p.y for p in current_object_points)]
                if current_object_points:
                    objects.append(GridObject(GridRegion(current_object_points), grid))

    return objects
    

def move_object(object_to_move: GridObject, x: int, y: int, grid) -> list[list[int]]:
    # x, y = object_to_move.region.x1 + dx, object_to_move.region.y1 + dy
    # copy the value of the object_to_move to the new position
    logger.debug(f"Moving object {object_to_move} to {x}, {y}")
    old_grid = copy.deepcopy(object_to_move.parent_grid)

    for i in range(object_to_move.region.x1, object_to_move.region.x2 + 1):
        for j in range(object_to_move.region.y1, object_to_move.region.y2 + 1):
            value = old_grid[j][i]
            if value != 0:
                grid[j+y][i+x] = value
    return grid

if __name__ == "__main__":
    file = r'"C:/Users/smart/Desktop/arc - local/main.py"'
    import os
    os.system(f'python {file}')

    