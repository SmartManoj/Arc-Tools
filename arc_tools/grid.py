from collections import Counter, deque
from enum import Enum
import json
import numpy as np
import logging
from copy import deepcopy
from arc_tools.plot import plot_grid
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MyEnum(Enum):
    def __repr__(self):
        return f"{self.__class__.__name__}.{self.name}"

class Color(MyEnum):
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
    
    def __eq__(self, other):
        return self.x1 == other.x1 and self.x2 == other.x2 and self.y1 == other.y1 and self.y2 == other.y2

    def __str__(self):
        return f"[(x1/y1)=({self.x1}/{self.y1}), (x2/y2)=({self.x2}/{self.y2})]"

class Grid(list):
    def __init__(self, grid: list[list[int]]):
        if type(grid) == Grid:
            raise ValueError(f"Wrong input type: {type(grid)}")
        if grid:
            super().__init__(deepcopy(grid))
            self.background_color = self.detect_background_color()
            self.n_rows = len(self)
            self.n_cols = len(self[0])
    
    def replace_color(self, old_color, new_color):
        for row in range(self.n_rows):
            for col in range(self.n_cols):
                if self[row][col] == old_color:
                    self[row][col] = new_color

    def remove_object(self, obj: 'SubGrid'):
        for row in range(obj.region.y1, obj.region.y2 + 1):
            for col in range(obj.region.x1, obj.region.x2 + 1):
                self[row][col] = self.background_color
    
    def copy(self):
        c = deepcopy(self)
        c.background_color = self.background_color
        return c
    
    def get_values_count(self, all: bool = False) -> Counter:
        values : Counter = Counter()
        for row in self:
            for col in row:
                if col != self.background_color or all:
                    values[col] += 1
        return values

    def detect_background_color(self):
        # maximum value in the grid
        self.background_color = None
        return self.get_max_value()

    def get_min_value(self):
        min_key, _ = min(self.get_values_count().items(), key=lambda x: x[1])
        return min_key
    
    def get_max_value(self):
        max_key, _ = max(self.get_values_count().items(), key=lambda x: x[1])
        return max_key
    
    def __eq__(self, other):
        return super().__eq__(other)
    
    def __ne__(self, other):
        return not self.__eq__(other)

    def save(self, name: str = "grid.json"):
        data = json.dumps(list(self))
        with open(name, 'w') as f:
            f.write(data)

class SubGrid(Grid):
    def __init__(self, region: GridRegion, parent_grid: Grid):
        self.region = region # Keep the attribute name 'region' for consistency
        self.parent_grid = parent_grid
        self.n_rows = self.region.y2 - self.region.y1 + 1
        self.n_cols = self.region.x2 - self.region.x1 + 1
        super().__init__(self.get_subgrid())
        self.background_color = self.parent_grid.background_color

    def __str__(self):
        return f"Region: {self.region}, n_rows: {self.n_rows}, n_cols: {self.n_cols}, background_color: {self.background_color}\n{super().__str__()}"
    
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
        for row in range(self.region.y1, self.region.y2 + 1):
            for col in range(self.region.x1, self.region.x2 + 1):
                if self.parent_grid[row][col] == value:
                    positions.append(GridPoint(col, row))
        return positions
    
    
                    
    def copy(self):
        return deepcopy(self)

    def get_points_and_sides_of_dots(self, value):
        points = self.get_points_of_dots(value)
        points_and_sides = []
        for point in points:
            points_and_sides.append((point, self.get_border_sides(point)))
        return points_and_sides
    
    def get_subgrid(self):
        grid = [[0 for _ in range(self.region.x2 - self.region.x1 + 1)] for _ in range(self.region.y2 - self.region.y1 + 1)]
        for row in range(self.region.y1, self.region.y2 + 1):
            for col in range(self.region.x1, self.region.x2 + 1):
                grid[row - self.region.y1][col - self.region.x1] = self.parent_grid[row][col]
        return grid
    
    def get_full_grid(self) -> Grid:
        n_parent_rows, n_parent_cols = len(self.parent_grid), len(self.parent_grid[0])
        grid = [[self.parent_grid.background_color for _ in range(n_parent_cols)] for _ in range(n_parent_rows)]
        for row in range(self.n_rows):
            for col in range(self.n_cols):
                grid[row + self.region.y1][col + self.region.x1] = self[row][col]
        return Grid(grid)
    
    def has_yellow_block(self):
        return Color.YELLOW.value in self.get_unique_values()
    
    def get_unique_values(self):
        return list(self.get_values_count().keys())

    def has_hollow_space(self):
        """
        Checks if a grid contains a 'hollow space' - a region of 0s
        completely surrounded by non-zero values.
        Uses BFS starting from border 0s to find all externally connected 0s.
        Any remaining 0s are considered internal/hollow.
        """
        return self.get_holes_count(max_count=1)
    
    def get_holes_count(self, max_count: int | None = None) -> int:
        if not self or not self[0]:
            return False # Handle empty or invalid grid

        rows, cols = len(self), len(self[0])
        visited = [[False for _ in range(cols)] for _ in range(rows)]
        q : deque[tuple[int, int]] = deque()

        # Add border 0s to the queue and mark as visited
        for r in range(rows):
            # Left border
            if self[r][0] == 0 and not visited[r][0]:
                q.append((r, 0))
                visited[r][0] = True
            # Right border
            if self[r][cols - 1] == 0 and not visited[r][cols - 1]:
                q.append((r, cols - 1))
                visited[r][cols - 1] = True

        for c in range(cols): # Avoid double-adding corners
            # Top border
            if self[0][c] == 0 and not visited[0][c]:
                q.append((0, c))
                visited[0][c] = True
            # Bottom border
            if self[rows - 1][c] == 0 and not visited[rows - 1][c]:
                q.append((rows - 1, c))
                visited[rows - 1][c] = True

        while q:
            r, c = q.popleft()
            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and \
                self[nr][nc] == self.background_color and not visited[nr][nc]:
                    visited[nr][nc] = True
                    q.append((nr, nc))

        count = 0
        for r in range(rows):
            for c in range(cols):
                if self[r][c] == self.background_color and not visited[r][c]:
                    count += 1
                    if max_count and count == max_count:
                        return count

        return 0 
    


def find_square_boxes(grid: Grid, size: int) -> list[SubGrid]:
    grid = deepcopy(grid)
    rows = len(grid)
    cols = len(grid[0])
    regions = []

    for r in range(rows - size + 1):
        for c in range(cols - size + 1):
            is_box = True
            for dr in range(size):
                for dc in range(size):
                    if grid[r + dr][c + dc] == grid.background_color:
                        is_box = False
                        break
                if not is_box:
                    break
            start_point = GridPoint(c, r)
            end_point = GridPoint(c + size - 1, r + size - 1)
            if is_box and grid[start_point.y][start_point.x] == grid[end_point.y][end_point.x]:
                regions.append(GridRegion([start_point, end_point]))
                for dr in range(size):
                    for dc in range(size):
                        grid[r + dr][c + dc] = 0

    return [SubGrid(region, grid) for region in regions]


def detect_objects(grid: Grid, required_object: str | None = None, invert: bool = False) -> list[SubGrid]:
    grid_np = np.array(grid)
    rows, cols = grid_np.shape
    visited = np.zeros_like(grid_np, dtype=bool)
    objects = []
    comp = '__eq__' if invert else '__ne__'
    for r in range(rows):
        for c in range(cols):
            if getattr(grid_np[r, c], comp)(grid.background_color) and not visited[r, c]:
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
                           getattr(grid_np[nr, nc], comp)(grid.background_color) and not visited[nr, nc]:
                            visited[nr, nc] = True
                            q.append((nr, nc))
                
                # filter only the corner points
                current_object_points = [
                    p for p in current_object_points 
                    if p.x == min(p.x for p in current_object_points) 
                    or p.x == max(p.x for p in current_object_points) 
                    or p.y == min(p.y for p in current_object_points) 
                    or p.y == max(p.y for p in current_object_points)
                ]
                if current_object_points:
                    obj = SubGrid(GridRegion(current_object_points), grid)
                    if required_object == 'square':
                        if obj.n_rows == 5 and obj.n_cols == 5:
                            objects.append(obj)
                        else:
                            new_objects = find_square_boxes(obj.get_full_grid(), 5)
                            logger.debug(f"Found {len(new_objects)} square boxes")
                            for new_obj in new_objects:
                                objects.append(new_obj)
                    else:
                        objects.append(obj)

    return objects
    

def move_object(object_to_move: SubGrid, x: int, y: int, grid: Grid) -> Grid:
    # x, y = object_to_move.region.x1 + dx, object_to_move.region.y1 + dy
    # copy the value of the object_to_move to the new position
    grid = grid
    logger.debug(f"Moving object {object_to_move} to {x}, {y}")
    old_grid = deepcopy(object_to_move.parent_grid)

    for row in range(object_to_move.region.y1, object_to_move.region.y2 + 1):
        for col in range(object_to_move.region.x1, object_to_move.region.x2 + 1):
            value = old_grid[row][col]
            if value != 0:
                grid[row+y][col+x] = value
    return Grid(grid)

if __name__ == "__main__":
    file = r'"C:/Users/smart/Desktop/arc - local/main.py"'
    import os
    # os.system(f'python {file}')
    g=[[2, 2, 2, 2, 2], [2, 1, 5, 2, 0], [2, 8, 9, 0, 0], [2, 2, 0, 0, 0], [2, 0, 0, 0, 0]]
    grid = Grid(g)
    grid2 = grid.copy()
    grid2[0][0] = 0
    print(grid)
    print(grid2)
    print(grid==grid2)