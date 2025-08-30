from collections import Counter, deque
from enum import Enum
import json
import numpy as np
from copy import deepcopy
from typing import Optional

from arc_tools.constants import CARDINAL_DIRECTIONS, EIGHT_DIRECTIONS
from arc_tools.logger import logger
from arc_tools.plot import plot_grids

class MyEnum(Enum):
    def __repr__(self):
        return f"{self.__class__.__name__}.{self.name}"

class Color(MyEnum):
    TEMP = -1
    BLACK = 0
    BLUE = 1
    RED = 2
    GREEN = 3
    YELLOW = 4
    LIGHT_GRAY = 5
    MAGENTA = 6
    ORANGE = 7
    LIGHT_BLUE = 8
    MAROON = 9


class FrameColor(MyEnum):
    WHITE = 0
    LIGHT_GRAY = 1
    GRAY = 2
    DARK_GRAY = 3
    CHARCOAL = 4
    BLACK = 5
    MAGENTA = 6
    PINK = 7
    RED = 8
    BLUE = 9
    SKY_BLUE = 10
    YELLOW = 11
    ORANGE = 12
    MAROON = 13
    GREEN = 14
    PURPLE = 15


class BorderSide(MyEnum):
    LEFT = 'left'
    RIGHT = 'right'
    TOP = 'top'
    BOTTOM = 'bottom'

class GridPoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    # iterable
    def __iter__(self):
        return iter((self.x, self.y))
    
    def __next__(self):
        return next(self.x, self.y)
    
    def __repr__(self):
        return f"({self.x}, {self.y})"
    
    def __eq__(self, other):
        if isinstance(other, GridPoint):
            return self.x == other.x and self.y == other.y
        elif isinstance(other, tuple):
            return self.x == other[0] and self.y == other[1]
        return False
    
    def __hash__(self):
        return hash((self.x, self.y))
    
    def __contains__(self, other):
        if isinstance(other, GridPoint):
            return self.x == other.x and self.y == other.y
        elif isinstance(other, tuple):
            return self.x == other[0] and self.y == other[1]
        return False

    def distance(self, other):
        return (self.x - other.x), (self.y - other.y)
    
    def manhattan_distance(self, other):
        return abs(self.x - other.x) + abs(self.y - other.y)

class GridRegion:
    def __init__(self, points: list[GridPoint]):
        self.x1 = min(p.x for p in points)
        self.x2 = max(p.x for p in points)
        self.y1 = min(p.y for p in points)
        self.y2 = max(p.y for p in points)
        self.width = self.x2 - self.x1 + 1
        self.height = self.y2 - self.y1 + 1
        self.start = GridPoint(self.x1, self.y1)
        self.end = GridPoint(self.x2, self.y2)
    
    def __eq__(self, other):
        return self.x1 == other.x1 and self.x2 == other.x2 and self.y1 == other.y1 and self.y2 == other.y2

    def __repr__(self):
        return f"[(x1/y1)=({self.x1}/{self.y1}), (x2/y2)=({self.x2}/{self.y2})]"
    
    def __hash__(self):
        return hash((self.x1, self.x2, self.y1, self.y2))
    
    def contains(self, obj):
        if isinstance(obj, Grid):
            return self.contains(obj.region)
        if isinstance(obj, GridPoint):
            return self.x1 <= obj.x <= self.x2 and self.y1 <= obj.y <= self.y2
        elif isinstance(obj, GridRegion):
            return self.x1 <= obj.x1 <= self.x2 and self.y1 <= obj.y1 <= self.y2 and self.x1 <= obj.x2 <= self.x2 and self.y1 <= obj.y2 <= self.y2
        return False
    
    def get_surrounding_points(self):
        new_x1 = self.x1 - 1
        new_y1 = self.y1 - 1
        new_x2 = self.x2 + 1
        new_y2 = self.y2 + 1
        new_region = GridRegion([GridPoint(new_x1, new_y1), GridPoint(new_x2, new_y2)])
        return new_region.get_border_points()

    def get_border_points(self):
        points = []
        for row in range(self.y1, self.y2 + 1):
            for col in range(self.x1, self.x2 + 1):
                if row == self.y1 or row == self.y2 or col == self.x1 or col == self.x2:
                    points.append(GridPoint(col, row))
        return points

class CustomIndexError(IndexError):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class SafeList(list):
    def __init__(self, grid: list[list[int]], allow_negative_index: bool = False):
        self.allow_negative_index = allow_negative_index
        super().__init__(grid)

    def __getitem__(self, index):
        try:
            if type(index) != int or (0 <= index < len(self) or (self.allow_negative_index and index < 0)):
                return super().__getitem__(index)
        except IndexError:
            # raise CustomIndexError(f"SafeList: Index {index} is out of bounds for list of length {len(self)}") from None
            pass
        return SafeList([])
    
    
    def __setitem__(self, index, value):
        try:
            return super().__setitem__(index, value)
        except IndexError:
            # raise CustomIndexError(f"SafeList assignment: Index {index} is out of bounds for list of length {len(self)}") from None
            pass
    
    

class Grid(SafeList):
    def __init__(self, grid: list[list[int]], background_color: int | None = None, allow_negative_index: bool = False, region: GridRegion | None = None):
        if type(grid) == Grid:
            raise ValueError(f"Wrong input type: {type(grid)}")
        grid = [SafeList(row, allow_negative_index) for row in grid]
        super().__init__(grid, allow_negative_index)
        if background_color is None:
            background_color = self.detect_background_color()
        self.background_color = background_color
        self.height = self.h = len(self)
        self.width = self.w = len(self[0])
        self.region = region or GridRegion([GridPoint(0, 0), GridPoint(self.width - 1, self.height - 1)])
        self.cx = self.region.x1 + self.region.width // 2
        self.cy = self.region.y1 + self.region.height // 2
    
    def is_solo(self, row: int, col: int):
        current_color = self[row][col]
        cardinal_cells = [self[row + dy][col + dx] for dx, dy in CARDINAL_DIRECTIONS]
        surrounding_cells = [self[row + dy][col + dx] for dx, dy in EIGHT_DIRECTIONS]
        return (sum(cell in [current_color, []] for cell in surrounding_cells) <= 3 and sum(cell in [current_color, []] for cell in cardinal_cells) <= 1) or all(cell != current_color for cell in surrounding_cells)
    
    def _shrink(self, factor):
        """Shrink a grid by the given factor while maintaining pattern structure."""
        if factor <= 1:
            return self
        
        rows = len(self)
        cols = len(self[0]) if self else 0
        
        new_rows = rows // factor
        new_cols = cols // factor
        
        shrunk = []
        for i in range(new_rows):
            row = []
            for j in range(new_cols):
                # Take the most common value in the factor x factor block
                values = []
                block = []
                start_row = i * factor
                start_col = j * factor
                for di in range(factor):
                    block_row = []
                    for dj in range(factor):
                        if start_row + di < rows and start_col + dj < cols:
                            value = self[start_row + di][start_col + dj]
                            values.append(value)
                            block_row.append(value)
                    if block_row:
                        block.append(block_row)
                
                # Check if all values in the block are the same
                if values:
                    if len(set(values)) != 1:
                        raise ValueError(f"Region ({start_col},{start_row}) to ({start_col+factor-1},{start_row+factor-1}) has different values:\n{block}")
                    row.append(values[0])
                else:
                    row.append(0)
            shrunk.append(row)
        
        return Grid(shrunk, self.background_color)

    
    def flatten_list(self):
        return [self[i][j] for i in range(self.height) for j in range(self.width)]
    
    def shrink(self, factor = None):
        """Find the maximum factor that can be used to shrink the grid by detecting pattern boundaries."""
        if factor:
            return self._shrink(factor)

        rows = len(self)
        cols = len(self[0]) if self else 0
        
        # Find the smallest repeating pattern size
        def find_pattern_size():
            # Check first row for pattern repetition
            first_row = self[0]
            first_element = first_row[0]
            
            # Count how many times the first element repeats
            repetition_count = 0
            for i in range(len(first_row)):
                if first_row[i] == first_element:
                    repetition_count += 1
                else:
                    break
            
            return repetition_count
        
        pattern_size = find_pattern_size()
        
        # Use the pattern size as the factor, but ensure it divides the grid dimensions
        max_factor = min(pattern_size, rows, cols)
        
        # Find the largest factor that divides both rows and cols
        for factor in range(max_factor, 0, -1):
            if rows % factor == 0 and cols % factor == 0:
                try:
                    return self._shrink(factor)
                except ValueError:
                    continue
        
        return self

    def strip(self):
        # remove all empty rows and columns
        starting_row_point = 0
        for row_idx in range(self.height):
            if all(cell == self.background_color for cell in self[row_idx]):
                starting_row_point += 1
            else:
                break
        ending_row_point = self.height - 1
        for row_idx in reversed(range(self.height)):
            if all(cell == self.background_color for cell in self[row_idx]):
                ending_row_point -= 1
            else:
                break
        starting_col_point = 0
        for col_idx in range(self.width):
            if all(row[col_idx] == self.background_color for row in self):
                starting_col_point += 1 
            else:
                break
        ending_col_point = self.width - 1
        for col_idx in reversed(range(self.width)):
            if all(row[col_idx] == self.background_color for row in self):
                ending_col_point -= 1
            else:
                break
        data = [row[starting_col_point:ending_col_point + 1] for row in self[starting_row_point:ending_row_point + 1]]
        return Grid(data, self.background_color)
    
    def __hash__(self) -> int: # type: ignore
        return hash((tuple(tuple(row) for row in self), self.background_color))
    
    def is_hole(self, region: GridRegion):
        logger.info(f"Checking if {region} is a hole")
        for row in range(region.y1 - 1, region.y2 + 2):
            for col in range(region.x1 - 1, region.x2 + 2):
                # if edge not background color, then it is not a hole
                if row == region.y1 - 1 or row == region.y2 + 1 or col == region.x1 - 1 or col == region.x2 + 1:
                    if self[row][col] == self.background_color:
                        logger.info(f"Edge {row},{col} is background color")
                        return False
                else:
                    if self[row][col] != self.background_color:
                        logger.info(f"Internal {row},{col} is not background color")
                        return False
        return True
    
    def as_sub_grid(self):
        return SubGrid(GridRegion([GridPoint(0, 0), GridPoint(self.width - 1, self.height - 1)]), self)

    def is_similar(self, other, ignore_color = False):
        if self.height > self.width:
            self = self.rotate()
        if other.height > other.width:
            other = other.rotate()
        if not isinstance(other, Grid):
            return False
        # if height and width are the same, then compare the points
        if self.height == other.height and self.width == other.width:
            def check(self, other):
                for row in range(self.height):
                    for col in range(self.width):
                        if ignore_color:
                            c1 = self[row][col] == self.background_color
                            c2 = other[row][col] == other.background_color
                            if c1 != c2:
                                return False
                        else:
                            if self[row][col] != other[row][col]:
                                return False
                return True
            
            # check all rotatations
            for _ in range(4):
                for _ in range(4):
                    if check(self, other):
                        return True
                    other = other.rotate()
                self = self.rotate()
        return False
    
    def rotate(self) -> 'Grid':
        """
        Rotates 90 degrees clockwise.
        """
        rows = self.height
        cols = self.width
        new_grid = [[self[rows-1-j][i] for j in range(rows)] for i in range(cols)]
        if type(self) == SubGrid:
            return SubGrid(GridRegion([GridPoint(0, 0), GridPoint(rows-1, cols-1)]), Grid(new_grid, self.background_color), self.color)
        else:
            return Grid(new_grid, self.background_color)

    def anti_rotate(self) -> 'Grid':
        """
        Rotate 90 degrees counter-clockwise.
        """
        rows = self.height
        cols = self.width
        new_grid = [[self[j][cols-1-i] for j in range(rows)] for i in range(cols)]
        if type(self) == SubGrid:
            return SubGrid(GridRegion([GridPoint(0, 0), GridPoint(rows-1, cols-1)]), Grid(new_grid, self.background_color), self.color)
        else:
            return Grid(new_grid, self.background_color)
    
    def flip_horizontally(self) -> 'Grid':
        rows = self.height
        cols = self.width
        new_grid = [self[rows-1-j] for j in range(rows)]
        if type(self) == SubGrid:
            g = Grid(new_grid, self.background_color)
            return SubGrid(GridRegion([GridPoint(0, 0), GridPoint(cols-1, rows-1)]), g, self.color)
        else:
            return Grid(new_grid, self.background_color)

    def flip_vertically(self) -> 'Grid':
        rows = self.height
        cols = self.width
        new_grid = [[self[j][cols-1-i] for i in range(cols)] for j in range(rows)]
        if type(self) == SubGrid:
            return SubGrid(GridRegion([GridPoint(0, 0), GridPoint(cols-1, rows-1)]), Grid(new_grid, self.background_color), self.color)
        else:
            return Grid(new_grid, self.background_color)

    def get(self, x: int, y: int) -> int:
        return self[y][x]
    
    def set(self, x: int, y: int, value: int):
        self[y][x] = value

    def get_top_side(self):
        return [self[0][i] for i in range(self.width)]
    
    def get_bottom_side(self):
        return [self[self.height - 1][i] for i in range(self.width)]
    
    def get_left_side(self):
        return [self[i][0] for i in range(self.height)]
    
    def get_right_side(self):
        return [self[i][self.width - 1] for i in range(self.height)]
    
    def get_side_data(self, side: BorderSide):
        if side == BorderSide.TOP:
            return self.get_top_side()
        elif side == BorderSide.BOTTOM:
            return self.get_bottom_side()
        elif side == BorderSide.LEFT:
            return self.get_left_side()
        elif side == BorderSide.RIGHT:
            return self.get_right_side()

    @property
    def area(self):
        return self.width * self.height
    
    def contains(self, other):
        return self.region.contains(other)
    
    def get_corner_colors(self):
        top_left = self[0][0]
        top_right = self[0][self.width - 1]
        bottom_left = self[self.height - 1][0]
        bottom_right = self[self.height - 1][self.width - 1]
        return [top_left, top_right, bottom_left, bottom_right]
    
    def compare(self, other):
        if len(self) != len(other):
            logger.info(f"Row length mismatch: Expected: {len(self)}, Actual: {len(other)}")
            return False
        for i in range(len(self)):
            if self[i] != other[i]:
                if len(self[i]) != len(other[i]):
                    logger.info(f"Column length mismatch for row {i+1}: Expected: {len(self[i])}, Actual: {len(other[i])}")
                    return False
                for j in range(len(self[i])):
                    if self[i][j] != other[i][j]:
                        logger.info(f"Mismatch at index row {i}, col {j}: Expected: {self[i][j]}, Actual: {other[i][j]}")
                        return False
        return True
    
    def replace_color(self, old_color: Color, new_color: Color, replace_in_parent_grid: Optional[bool] = None):
        if replace_in_parent_grid is None:
            replace_in_parent_grid = type(self) == SubGrid
        if replace_in_parent_grid:
            for row in range(self.region.y1, self.region.y2 + 1):
                for col in range(self.region.x1, self.region.x2 + 1):
                    if self.parent_grid[row][col] == old_color.value:
                        self.parent_grid[row][col] = new_color.value
        else:
            for row in range(self.height):
                for col in range(self.width):
                    if self[row][col] == old_color.value:
                        self[row][col] = new_color.value
        self.colors = self.get_unique_values()
        return self
    
    def replace_all_color(self, new_color):
        for row in range(self.height):
            for col in range(self.width):
                if self[row][col] != self.background_color:
                    self[row][col] = new_color
        return self
    
    def fill_color(self, point: GridPoint, new_color: int):
        # use bfs to fill the color
        queue = deque([point])
        old_color = self[point.y][point.x]
        while queue:
            point = queue.popleft()
            if self[point.y][point.x] == new_color:
                continue
            old_color = self[point.y][point.x]
            self[point.y][point.x] = new_color
            for dx, dy in EIGHT_DIRECTIONS:
                new_col = point.x + dx
                new_row = point.y + dy
                if 0 <= new_col < self.width and 0 <= new_row < self.height:
                    if self[new_row][new_col] == old_color:
                        queue.append(GridPoint(new_col, new_row))

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
        return Grid([[self[row][col] for col in range(region.x1, region.x2 + 1)] for row in range(region.y1, region.y2 + 1)], self.background_color)

    def remove_object(self, obj: 'SubGrid', background_color: int | None = None):
        if background_color is None:
            background_color = self.background_color
        for row in range(obj.height):
            for col in range(obj.width):
                if obj[row][col] != background_color:
                    self[row+obj.region.y1][col+obj.region.x1] = background_color
        return self

    def copy(self):
        new_grid_data = [list(row) for row in self]
        return Grid(new_grid_data, self.background_color, self.allow_negative_index)
    
    def get_frame(self):
        # set all dots to background color
        copy = self.copy()
        for row in range(self.height):
            for col in range(self.width):
                if copy[row][col] != self.background_color:
                    copy[row][col] = self.background_color
        return copy

    def get_values_count(self, all: bool = False) -> Counter:
        values : Counter = Counter()
        for row in self:
            for col in row:
                if col != getattr(self, "background_color", None) or all:
                    values[col] += 1
        return values
    
    def has_yellow_block(self):
        return Color.YELLOW.value in self.get_unique_values()
    
    def get_unique_values(self):
        return sorted(list(self.get_values_count().keys()))
    

    def get_total_dots(self) -> int:
        return sum(self.get_values_count().values())
    
    def get_total_unique_dots(self) -> int:
        return len(self.get_unique_values())

    def detect_background_color(self) -> int:
        # maximum value in the grid
        # color_counts = self.get_values_count()
        # most_common_values = list(key for key, _ in color_counts.most_common(2))
        # if Color.BLACK.value in most_common_values and len(color_counts) > 2:
        #     return Color.BLACK.value
        return self.get_max_color()

    def get_min_color(self) -> int:
        min_key, _ = min(self.get_values_count().items(), key=lambda x: x[1], default=(None, 0))
        return min_key
    
    def get_max_color(self) -> int:
        max_key, _ = max(self.get_values_count().items(), key=lambda x: x[1], default=(None, 0))
        return max_key
    
    def __eq__(self, other):
        return super().__eq__(other)
    
    def __ne__(self, other):
        return not self.__eq__(other)

    def save(self, name: str = "grid.json"):
        data = json.dumps(list(self))
        with open(name, 'w') as f:
            f.write(data)

    def clear_corners(self, grid_size: int = 1, relative_to: Optional['SubGrid'] = None):
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
                    self[y][x] = self.background_color
        return self
    
    def extend_grid(self, new_height: int, new_width: int):
        """
        Extends the grid to at least new_height x new_width, filling new cells with background_color.
        """
        if new_height <= self.height and new_width <= self.width:
            return
        # Extend rows
        for row in self:
            if new_width > self.width:
                row.extend(SafeList([self.background_color] * (new_width - self.width)))
            if new_width < 0:
                row.insert(0, SafeList([self.background_color] * (-new_width)))
        
        self.width = len(self[0])

        # Add new rows if needed
        if new_height > self.height:
            for _ in range(self.height, new_height):
                self.append(SafeList([self.background_color] * self.width))
        if new_height < 0:
            for _ in range(-new_height):
                self.insert(0, SafeList([self.background_color] * self.width))

        self.height = len(self)
        
        return self 
    
    def display(self):
        max_digits = len(str(max(self.get_unique_values(), default=0)))
        for row in self:
            for col in row:
                print(f"{col:>{max_digits}}", end=" ")
            print()

class SubGrid(Grid):
    def __init__(self, region: GridRegion, parent_grid: Grid, obj_color: int | None = None, points: list[GridPoint] | None = None):
        self.parent_grid = parent_grid
        self.region = region
        self.points = points
        self.background_color = self.parent_grid.background_color
        super().__init__(self.get_subgrid(obj_color), self.background_color, allow_negative_index=True, region=region)
        self.height = self.h = self.region.y2 - self.region.y1 + 1
        self.width = self.w = self.region.x2 - self.region.x1 + 1
        self.color = obj_color
        self.colors = self.get_unique_values()
        if self.color is None:
            if len(self.colors) == 1:
                self.color = self.colors[0]

    def remove_border(self, border: int = 1):
        new_grid_region = GridRegion([GridPoint(self.region.x1 + border, self.region.y1 + border), GridPoint(self.region.x2 - border, self.region.y2 - border)])
        # BUG? passing self.color floods the grid with the color
        return SubGrid(new_grid_region, self.parent_grid, None)
    
    def __hash__(self) -> int: # type: ignore
        return hash((self.region, self.parent_grid, self.background_color))
    
    def new_region(self, dx1: int = 0, dy1: int = 0, dx2: int = 0, dy2: int = 0, region: GridRegion | None = None):
        if not region:
            region = GridRegion([GridPoint(self.region.x1 + dx1, self.region.y1 + dy1), GridPoint(self.region.x2 + dx2, self.region.y2 + dy2)])
        return SubGrid(region, self.parent_grid, self.color)

    def __repr__(self):
        return f"Region: {self.region}, height: {self.height}, width: {self.width}, background_color: {self.background_color}"
    
    def __eq__(self, other):
        if not isinstance(other, SubGrid):
            return False
        return (self.region == other.region and 
                self.parent_grid == other.parent_grid and 
                self.background_color == other.background_color and
                super().__eq__(other))
    
    
    
    def set_center_color(self):
        self.center_color = self.parent_grid[self.cy][self.cx]
        
    def expand(self, n: int = None):
        if n:
            x1 = x2 = y1 = y2 = n
        else:
            x1 = x2 = y1 = y2 = 0
            # check for x1
            for col in reversed(range(self.region.x1)):
                if any(self.parent_grid[row][col] != self.background_color for row in range(self.region.y1, self.region.y2 + 1)):
                    x1 = self.region.x1 - col - 1
                    break
            for col in range(self.region.x2 + 1, self.parent_grid.width):
                if any(self.parent_grid[row][col] != self.background_color for row in range(self.region.y1, self.region.y2 + 1)):
                    x2 = col - self.region.x2 - 1
                    break
            for row in reversed(range(self.region.y1)):
                if any(self.parent_grid[row][col] != self.background_color for col in range(self.region.x1, self.region.x2 + 1)):
                    y1 = self.region.y1 - row - 1
                    break   
            for row in range(self.region.y2 + 1, self.parent_grid.height):
                if any(self.parent_grid[row][col] != self.background_color for col in range(self.region.x1, self.region.x2 + 1)):
                    y2 = row - self.region.y2 - 1
                    break
            
        return SubGrid(GridRegion([
            GridPoint(max(self.region.x1 - x1, 0), max(self.region.y1 - y1, 0)),
            GridPoint(min(self.region.x2 + x2, self.parent_grid.width - 1), min(self.region.y2 + y2, self.parent_grid.height - 1))
        ]), self.parent_grid, self.color)
    
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
    
    def get_position_of_dot(self, value):
        positions = []
        for row in range(self.region.y1, self.region.y2 + 1):
            for col in range(self.region.x1, self.region.x2 + 1):
                if self.parent_grid[row][col] == value:
                    positions.append(GridPoint(col, row))
        return positions
    
    
                    
    def copy(self):
        return deepcopy(self)

    def get_points_and_sides_of_dots(self, value):
        points = self.get_position_of_dot(value)
        points_and_sides = []
        for point in points:
            points_and_sides.append((point, self.get_border_sides(point)))
        return points_and_sides
    
    def get_subgrid(self, obj_color: int | None = None, safe: bool = True):
        cls = SafeList if safe else list
        grid = [cls([self.parent_grid.background_color for _ in range(self.region.x2 - self.region.x1 + 1)]) for _ in range(self.region.y2 - self.region.y1 + 1)]
        for row in range(self.region.y1, self.region.y2 + 1):
            for col in range(self.region.x1, self.region.x2 + 1):
                if obj_color is None or self.parent_grid[row][col] == obj_color:
                    grid[row - self.region.y1][col - self.region.x1] = self.parent_grid[row][col]
        return cls(grid)
    
    def get_full_grid(self) -> Grid:
        n_parent_rows, n_parent_cols = len(self.parent_grid), len(self.parent_grid[0])
        grid = [[self.parent_grid.background_color for _ in range(n_parent_cols)] for _ in range(n_parent_rows)]
        for row in range(self.height):
            for col in range(self.width):
                grid[row + self.region.y1][col + self.region.x1] = self[row][col]
        return Grid(grid, self.background_color)

    def has_hollow_space(self):
        """
        Checks if a grid contains a 'hollow space' - a region of 0s
        completely surrounded by non-zero values.
        Uses BFS starting from border 0s to find all externally connected 0s.
        Any remaining 0s are considered internal/hollow.
        """
        return self.get_holes_count(max_count=1)
    
    def get_holes_count(self, max_count: int | None = None) -> int:
        rows, cols = len(self), len(self[0])
        visited = [[False for _ in range(cols)] for _ in range(rows)]
        q : deque[tuple[int, int]] = deque()

        for r in range(rows):
            # Left border
            if self[r][0] == self.background_color and not visited[r][0]:
                q.append((r, 0))
                visited[r][0] = True
            # Right border
            if self[r][cols - 1] == self.background_color and not visited[r][cols - 1]:
                q.append((r, cols - 1))
                visited[r][cols - 1] = True

        for c in range(cols): # Avoid double-adding corners
            # Top border
            if self[0][c] == self.background_color and not visited[0][c]:
                q.append((0, c))
                visited[0][c] = True
            # Bottom border
            if self[rows - 1][c] == self.background_color and not visited[rows - 1][c]:
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

        return count
    


def split_into_square_boxes(grid: Grid, size: int, obj_color: int | None = None) -> list[SubGrid]:
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
                        grid[r + dr][c + dc] = grid.background_color

    return [SubGrid(region, grid, obj_color) for region in regions]

class Shape:
    pass

class Square(Shape):
    def __init__(self, size: int | None = None):
        self.size = size
        
        

def detect_objects(grid: Grid, required_object: Shape | None = None, invert: bool = False, required_color: Color | None = None, ignore_color: Color | None = None, single_color_only: bool = False, go_diagonal: bool = True, max_count: int | None = None, ignore_corners: bool = False, point: GridPoint | None = None) -> list[SubGrid]:
    grid_np = np.array(grid)
    rows, cols = grid_np.shape
    visited = np.zeros_like(grid_np, dtype=bool)
    objects = []
    is_subgrid = type(grid) == SubGrid
    x_offset = grid.region.x1 if is_subgrid else 0
    y_offset = grid.region.y1 if is_subgrid else 0
    if is_subgrid:
        grid = Grid(grid, grid.background_color)
    def compare(a):
        val = a != grid.background_color
        if ignore_color:
            val = val and a != ignore_color.value
        if required_color:
            val = val and a == required_color.value
        if invert:
            return not val
        return val
    
    for r in range(rows):
        for c in range(cols):
            if point:
                r, c = point.y, point.x
            current_color = grid[r][c]
            if compare(current_color) and not visited[r, c]:
                # Start BFS for a new object
                current_object_points = []
                q = deque([(r, c)])
                visited[r, c] = True
                
                while q:
                    row, col = q.popleft()
                    current_object_points.append(GridPoint(col, row)) # x=col, y=row
                    if go_diagonal:
                        directions = EIGHT_DIRECTIONS
                    else:
                        directions = CARDINAL_DIRECTIONS
                    for dr, dc in directions:
                        nr, nc = row + dr, col + dc
                        if 0 <= nr < rows and 0 <= nc < cols and \
                           compare(grid_np[nr, nc]) and not visited[nr, nc]:
                            if single_color_only and grid_np[nr, nc] != current_color:
                                continue
                            if max_count and len(current_object_points) >= max_count:
                                break
                            visited[nr, nc] = True
                            q.append((nr, nc))
                
                if is_subgrid:
                    # add x1 and y1 to current_object_points
                    current_object_points = [GridPoint(p.x + x_offset, p.y + y_offset) for p in current_object_points]
                    
                # filter only the corner points
                current_object_corner_points = [
                    p for p in current_object_points
                    if p.x == min(p.x for p in current_object_points)
                    or p.x == max(p.x for p in current_object_points)
                    or p.y == min(p.y for p in current_object_points)
                    or p.y == max(p.y for p in current_object_points)
                ]
                if current_object_corner_points:
                    region = GridRegion(current_object_points)
                    if ignore_corners:
                        if region.x1 == 0 or region.y1 == 0 or region.x2 == grid.width - 1 or region.y2 == grid.height - 1:
                            continue
                    obj_color = current_color if single_color_only else None
                    obj = SubGrid(region, grid, obj_color, points=current_object_points)
                    if isinstance(required_object, Square):
                        size = required_object.size
                        if not size:
                            size = obj.height
                        if obj.height == size and obj.width == size and list(obj.get_values_count().values())[0] == obj.area:
                            objects.append(obj)
                        else:
                            new_objects = split_into_square_boxes(obj.get_full_grid(), size, obj_color)
                            logger.debug(f"Found {len(new_objects)} square boxes")
                            for new_obj in new_objects:
                                if new_obj.height == size and new_obj.width == size:
                                    objects.append(new_obj)
                    else:
                        objects.append(obj)
                    if point:
                        break
    logger.debug(f"Found {len(objects)} objects")
    return objects
    
    
def move_object(object_to_move: SubGrid, dx: int, dy: int, grid: Grid, extend_grid: bool = False, fill_color: Color | None = None) -> SubGrid:
    """
    Moves the object_to_move by (dx, dy) in the grid, extending the grid if necessary.
    """
    if dx == 0 and dy == 0:
        return object_to_move
    logger.debug(f"Moving object {object_to_move} by {dx}, {dy}")
    grid.remove_object(object_to_move, fill_color.value if fill_color else None)
    return copy_object(object_to_move, dx, dy, grid, extend_grid, silent=True)

def place_object_on_new_grid(object_to_place: SubGrid, x: int, y: int, grid: Grid, fill_color: int | None = None) -> SubGrid:
    """
    Places the object_to_place at (x, y) in the grid, extending the grid if necessary.
    """
    logger.debug(f"Placing object {object_to_place} at {x}, {y}")
    for row in range(object_to_place.height):
        for col in range(object_to_place.width):
            if object_to_place[row][col] != object_to_place.background_color:
                if fill_color:
                    grid[y+row][x+col] = fill_color
                else:
                    grid[y+row][x+col] = object_to_place[row][col]
    return SubGrid(GridRegion([GridPoint(x, y), GridPoint(x + object_to_place.width - 1, y + object_to_place.height - 1)]), grid, object_to_place.color)

def place_object(object_to_place: SubGrid, x: int, y: int, grid: Grid, remove_object: bool = True) -> SubGrid:
    """
    Places the object_to_place at (x, y) in the grid, extending the grid if necessary.
    """
    dx = x - object_to_place.region.x1
    dy = y - object_to_place.region.y1
    if remove_object:
        grid.remove_object(object_to_place)
    return move_object(object_to_place, dx, dy, grid)


def copy_object(object_to_copy: SubGrid, dx: int, dy: int, grid: Grid, extend_grid: bool = False, greedy: bool = True, silent: bool = False) -> SubGrid:
    """
    Copies the object_to_copy by (dx, dy) in the grid, extending the grid if necessary.
    """
    if not silent:
        logger.debug(f"Copying object {object_to_copy} by {dx}, {dy} in grid of type {type(grid)}")
    if extend_grid:
        # Calculate new bounds
        min_row = object_to_copy.region.y1 + dy
        min_col = object_to_copy.region.x1 + dx
        max_row = object_to_copy.region.y2 + dy
        max_col = object_to_copy.region.x2 + dx
        # Extend grid if needed
        required_height = max(max_row + 1, grid.height)
        required_width = max(max_col + 1, grid.width)
        if required_height > grid.height or required_width > grid.width:
            grid.extend_grid(required_height, required_width)
        
        # negative extend grid
        if min_row < 0 or min_col < 0:
            grid.extend_grid(-min_row, -min_col)
    # copy the object

    dx1, dy1 = object_to_copy.region.x1 + dx, object_to_copy.region.y1 + dy
    for row in range(object_to_copy.height):
        for col in range(object_to_copy.width):
            value = object_to_copy[row][col]
            row_index = row + dy1
            col_index = col + dx1
            if value != grid.background_color:
                if 0 <= row_index < len(grid) and 0 <= col_index < len(grid[0]):
                    if greedy or grid[row_index][col_index] == grid.background_color:
                        grid[row_index][col_index] = value

    copied_obj = object_to_copy.copy()
    copied_obj.region.x1 = max(copied_obj.region.x1 + dx, 0)
    copied_obj.region.x2 = min(copied_obj.region.x2 + dx, grid.width - 1)
    copied_obj.region.y1 = max(copied_obj.region.y1 + dy, 0)
    copied_obj.region.y2 = min(copied_obj.region.y2 + dy, grid.height - 1)
    return copied_obj


def flip_horizontally(object: Grid) -> Grid:
    pass

def flip_vertically(object: Grid) -> Grid:
    pass


if __name__ == "__main__":
    # Create a test grid
    test_grid = Grid([
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
    ], background_color=0)
    sub_grid = SubGrid(GridRegion([GridPoint(1, 1), GridPoint(2, 2)]), test_grid)
    print(sub_grid.cx)
    exit()
    # Create a SubGrid from the colored region
    region = GridRegion([GridPoint(1, 1), GridPoint(2, 2)])
    test_object = SubGrid(region, test_grid)
    