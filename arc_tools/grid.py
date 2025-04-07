from collections import Counter, deque
from enum import Enum
import json
import numpy as np
import logging
from copy import deepcopy
from arc_tools.plot import plot_grid, plot_grids
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
    
    def __hash__(self):
        return hash((self.x, self.y))


class GridRegion:
    def __init__(self, points: list[GridPoint]):
        self.x1 = min(p.x for p in points)
        self.x2 = max(p.x for p in points)
        self.y1 = min(p.y for p in points)
        self.y2 = max(p.y for p in points)
        self.width = self.x2 - self.x1 + 1
        self.height = self.y2 - self.y1 + 1 
    
    def __eq__(self, other):
        return self.x1 == other.x1 and self.x2 == other.x2 and self.y1 == other.y1 and self.y2 == other.y2

    def __str__(self):
        return f"[(x1/y1)=({self.x1}/{self.y1}), (x2/y2)=({self.x2}/{self.y2})]"
    
    def __hash__(self):
        return hash((self.x1, self.x2, self.y1, self.y2))

class CustomIndexError(IndexError):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class SafeList(list):
    def __getitem__(self, index):
        try:
            return super().__getitem__(index)
        except IndexError:
            raise CustomIndexError(f"Index {index} is out of bounds for list of length {len(self)}") from None
        
    
    
    

class Grid(SafeList):
    def __init__(self, grid: list[list[int]]):
        if type(grid) == Grid:
            raise ValueError(f"Wrong input type: {type(grid)}")
        if grid:
            grid = deepcopy(grid)
            grid = [SafeList(row) for row in grid]
            super().__init__(grid)
            self.background_color = self.detect_background_color()
            self.height = len(self)
            self.width = len(self[0])
    
    def __hash__(self) -> int:
        return hash((tuple(tuple(row) for row in self), self.background_color))
    
    def compare(self, other):
        if len(self) != len(other):
            print(f"Length mismatch: {len(self)} != {len(other)}")
            return False
        for i in range(len(self)):
            if self[i] != other[i]:
                if len(self[i]) != len(other[i]):
                    print(f"Row length mismatch at index {i}: {len(self[i])} != {len(other[i])}")
                    return False
                for j in range(len(self[i])):
                    if self[i][j] != other[i][j]:
                        print(f"Mismatch at index {i}/{j}: {self[i][j]}, {other[i][j]}")
                        return False
        return True
    
    def replace_color(self, old_color, new_color):
        for row in range(self.height):
            for col in range(self.width):
                if self[row][col] == old_color:
                    self[row][col] = new_color
        return self
    
    def replace_dot(self, dot_color, obj: 'SubGrid', dx: int, dy: int, first_grid: 'Grid'):
        logger.debug(f"Replacing dot {dot_color} with object {obj} at {dx}, {dy}")
        for row in range(self.height):
            for col in range(self.width):
                if first_grid[row][col] == dot_color:
                    first_grid[row][col] = self.background_color
                    for obj_row in range(min(obj.height, self.height - row - dy)):
                        for obj_col in range(min(obj.width, self.width - col - dx)):
                            new_row = row + obj_row + dy
                            new_col = col + obj_col + dx
                            if new_row >= 0 and new_col >= 0:
                                if self[new_row][new_col] in [self.background_color, dot_color]:
                                    self[new_row][new_col] = obj[obj_row][obj_col]
        return self
    
    def crop(self, region: GridRegion):
        return Grid([[self[row][col] for col in range(region.x1, region.x2 + 1)] for row in range(region.y1, region.y2 + 1)])

    def remove_object(self, obj: 'SubGrid'):
        for row in range(obj.region.y1, obj.region.y2 + 1):
            for col in range(obj.region.x1, obj.region.x2 + 1):
                self[row][col] = self.background_color
        return self

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
    
    def has_yellow_block(self):
        return Color.YELLOW.value in self.get_unique_values()
    
    def get_unique_values(self):
        return list(self.get_values_count().keys())
    

    def get_total_dots(self) -> int:
        return sum(self.get_values_count().values())
    
    def get_total_unique_dots(self) -> int:
        return len(self.get_unique_values())

    def detect_background_color(self):
        # maximum value in the grid
        self.background_color = None
        most_common_values = list(key for key, _ in self.get_values_count().most_common(2))
        if Color.BLACK.value in most_common_values:
            return Color.BLACK.value
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

    def remove_corner_grid(self, grid_size=1, relative_to: 'SubGrid' = None):
        top_left_corner = GridPoint(0, 0)
        top_right_corner = GridPoint(0, len(self[0])-1 - grid_size + 1)
        bottom_left_corner = GridPoint(len(self)-1 - grid_size + 1, 0)
        bottom_right_corner = GridPoint(len(self)-1 - grid_size + 1, len(self[0])-1 - grid_size + 1)
        if relative_to:
            top_left_corner = GridPoint(relative_to.region.x1 - grid_size, relative_to.region.y1 - grid_size)
            top_right_corner = GridPoint(relative_to.region.x2 + 1, relative_to.region.y1 - grid_size)
            bottom_left_corner = GridPoint(relative_to.region.x1 - grid_size, relative_to.region.y2 + 1)
            bottom_right_corner = GridPoint(relative_to.region.x2 + 1, relative_to.region.y2 + 1)
        corners_list = [top_left_corner, top_right_corner, bottom_left_corner, bottom_right_corner]
        for corners in corners_list:
            for y in range(corners.y, corners.y + grid_size):
                for x in range(corners.x, corners.x + grid_size):
                    if y < 0 or x < 0 or y >= len(self) or x >= len(self[0]):
                        continue
                    self[y][x] = 0
        return self 
        

class SubGrid(Grid):
    def __init__(self, region: GridRegion, parent_grid: Grid):
        self.region = region # Keep the attribute name 'region' for consistency
        self.parent_grid = parent_grid
        super().__init__(self.get_subgrid())
        self.height = self.region.y2 - self.region.y1 + 1
        self.width = self.region.x2 - self.region.x1 + 1
        self.background_color = self.parent_grid.background_color

    def __hash__(self) -> int:
        return hash((self.region, self.parent_grid, self.background_color))
    
    def __str__(self):
        return f"Region: {self.region}, height: {self.height}, width: {self.width}, background_color: {self.background_color}"
    
    def expand(self, n: int):
        return SubGrid(GridRegion([
            GridPoint(max(self.region.x1 - n, 0), max(self.region.y1 - n, 0)),
            GridPoint(min(self.region.x2 + n, self.parent_grid.width - 1), min(self.region.y2 + n, self.parent_grid.height - 1))
        ]), self.parent_grid)
    
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
    
    def is_in_corner(self):
        top_left = (self.region.x1, self.region.y1)
        top_right = (self.region.x2, self.region.y1)
        bottom_left = (self.region.x1, self.region.y2)
        bottom_right = (self.region.x2, self.region.y2)
        parent_top_left = (0,0)
        parent_top_right = (self.parent_grid.width - 1,0)
        parent_bottom_left = (0,self.parent_grid.height - 1)
        parent_bottom_right = (self.parent_grid.width - 1,self.parent_grid.height - 1)
        return top_left == parent_top_left or \
               top_right == parent_top_right or \
               bottom_left == parent_bottom_left or \
               bottom_right == parent_bottom_right
    
    def get_corner_position(self, new_object: 'SubGrid'):
        top_left = (self.region.x1, self.region.y1)
        top_right = (self.region.x2, self.region.y1)
        bottom_left = (self.region.x1, self.region.y2)
        bottom_right = (self.region.x2, self.region.y2)
        parent_top_left = (0,0)
        parent_top_right = (self.parent_grid.width - 1,0)
        parent_bottom_left = (0,self.parent_grid.height - 1)
        parent_bottom_right = (self.parent_grid.width - 1,self.parent_grid.height - 1)
        if top_left == parent_top_left:
            return 0, 0
        elif top_right == parent_top_right:
            return self.parent_grid.width - new_object.width, 0
        elif bottom_left == parent_bottom_left:
            return 0, self.parent_grid.height - new_object.height
        elif bottom_right == parent_bottom_right:
            return self.parent_grid.width - new_object.width, self.parent_grid.height - new_object.height
        else:
            return new_object.region.x1, new_object.region.y1
    
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
        for row in range(self.height):
            for col in range(self.width):
                grid[row + self.region.y1][col + self.region.x1] = self[row][col]
        return Grid(grid)
    
    

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
    


def split_into_square_boxes(grid: Grid, size: int) -> list[SubGrid]:
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


def detect_objects(grid: Grid, required_object: str | None = None, invert: bool = False, required_color: Color | None = None, ignore_color: Color | None = None, single_color_only: bool = False) -> list[SubGrid]:
    grid_np = np.array(grid)
    rows, cols = grid_np.shape
    visited = np.zeros_like(grid_np, dtype=bool)
    objects = []
    
    def compare(a):
        val = a != grid.background_color
        if ignore_color:
            val = val and a != ignore_color
        if required_color:
            val = val and a == required_color
        if invert:
            return not val
        return val
    
    for r in range(rows):
        for c in range(cols):
            current_color = grid_np[r, c]
            if compare(current_color) and not visited[r, c]:
                # Start BFS for a new object
                current_object_points = []
                q = deque([(r, c)])
                visited[r, c] = True
                

                while q:
                    row, col = q.popleft()
                    current_object_points.append(GridPoint(col, row)) # x=col, y=row

                    # Check neighbors (8-connectivity: up, down, left, right, and diagonals)
                    for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
                        nr, nc = row + dr, col + dc
                        if 0 <= nr < rows and 0 <= nc < cols and \
                           compare(grid_np[nr, nc]) and not visited[nr, nc]:
                            if single_color_only and grid_np[nr, nc] != current_color:
                                continue
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
                        if obj.height == 5 and obj.width == 5:
                            objects.append(obj)
                        else:
                            new_objects = split_into_square_boxes(obj.get_full_grid(), 5)
                            logger.debug(f"Found {len(new_objects)} square boxes")
                            for new_obj in new_objects:
                                objects.append(new_obj)
                    else:
                        objects.append(obj)
    logger.debug(f"Found {len(objects)} objects")
    return objects
    

def move_object(object_to_move: SubGrid, dx: int, dy: int, grid: Grid) -> Grid:
    # x, y = object_to_move.region.x1 + dx, object_to_move.region.y1 + dy
    # copy the value of the object_to_move to the new position
    logger.debug(f"Moving object {object_to_move} to {dx}, {dy} in grid of type {type(grid)}")
    old_grid = deepcopy(object_to_move.get_full_grid())
    for row in range(object_to_move.region.y1, object_to_move.region.y2 + 1):
        for col in range(object_to_move.region.x1, object_to_move.region.x2 + 1):
            value = old_grid[row][col]
            if value != grid.background_color:
                if 0 <= row+dy < len(grid) and 0 <= col+dx < len(grid[0]):
                    grid[row+dy][col+dx] = value

    return grid

def rotate_object(object: SubGrid) -> SubGrid:
    """
    Rotate a object 90 degrees clockwise.
    
    Args:
        object: The object to rotate
        
    Returns:
        SubGrid: The rotated object
    """
    rows = object.height
    cols = object.width
    new_grid = [[object[rows-1-j][i] for j in range(rows)] for i in range(cols)]
    return SubGrid(GridRegion([GridPoint(0, 0), GridPoint(rows-1, cols-1)]), Grid(new_grid))

if __name__ == "__main__":
    file = r'"C:/Users/smart/Desktop/arc - local/main.py"'
    import os
    # os.system(f'python {file}')
    g=[[0, 0 ,1, 1, 2, 2, 0, 0]]
    print("Input grid:", g)
    output = detect_objects(Grid(g), single_color_only=1)
    # expected =  [[[1]], [[1]], [[2]]]
    expected =  [[[1, 2]]]
    print("Output:", output)
    print("Expected:", expected)
    print("Output type:", type(output))
    print("Expected type:", type(expected))
    print("Output length:", len(output))
    print("Expected length:", len(expected))
    if len(output) == len(expected):
        for i in range(len(output)):
            print(f"Output[{i}]:", output[i])
            print(f"Expected[{i}]:", expected[i])
            print(f"Values match:", [[[output[i][0][0]]]] == [expected[i]])
    assert [[[obj[0][0]]] for obj in output] == expected