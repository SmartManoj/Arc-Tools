from datetime import datetime
from arc_tools import grid
from arc_tools.logger import logger
from copy import deepcopy
from itertools import combinations
import os
from glob import glob
import json
from arc_tools.grid import Grid, GridPoint, GridRegion, detect_objects
from arc_tools.hollow_count import count_hollows_task
from arc_tools.check_fit import check_fit
from arc_tools.plot import plot_grid, plot_grids
from arc_tools.squash import squash_grid

show_count = 0

from collections import Counter, deque # Add deque import
from arc_tools.grid import SubGrid # Add SubGrid import

from typing import Sequence # Add typing imports

from arc_tools.grid import Color
from arc_tools.grid import move_object

def repeat_reverse_grid(grid: Grid) -> Grid:
    """
    Transform a grid by repeating the grid thrice horizontally and stack them vertically in (original, reversed, original) order.
    """
    result = []
    original_grids = []
    reversed_grids = []
    
    for row in grid:
        original = [x for _ in range(3) for x in row]
        original_grids.append(original)
        
        reversed_row = list(reversed(row))
        reversed_grid = [x for _ in range(3) for x in reversed_row]
        reversed_grids.append(reversed_grid)
    
    for _ in range(3):
        result.extend(original_grids)
        result.extend(reversed_grids)
    
    return Grid(result[:len(grid) * 3])

def move_object_without_collision(grid: Grid) -> Grid:
    global show_count
    objects = detect_objects(grid, required_object = 'square')
    blue_objects = [obj for obj in objects if obj[0][0]==Color.LIGHTBLUE.value]
    blue_objects.sort(key=lambda x: x.region.x1)
    red_objects = [obj for obj in objects if obj[0][0]==Color.RED.value]
    red_objects.sort(key=lambda x: x.region.x1, reverse=True)
    logger.info(f"Total objects: {len(objects)}, blue_objects: {len(blue_objects)}, red_objects: {len(red_objects)}")

    left_side_grid = grid.copy()
    # remove red object
    for obj in red_objects:
            left_side_grid.remove_object(obj)
    # move blue object to the left side
    # sort blue objects by x1
    
    for obj in blue_objects:
        for i in range(obj.region.x1):
            # Check if all rows in the object's height range have space
            all_rows_clear = True
            for y in range(obj.region.y1, obj.region.y2 + 1):
                if left_side_grid[y][i] != left_side_grid.background_color:
                    all_rows_clear = False
                    break
            
            if all_rows_clear:
                left_side_grid.remove_object(obj)
                left_side_grid = move_object(obj, -(obj.region.x1 - i), 0, left_side_grid)
                break
    right_side_grid = grid.copy()
    # remove blue object
    for obj in blue_objects:
        right_side_grid.remove_object(obj)
    # move red object to the right side
    for obj in red_objects:
        grid_width = len(right_side_grid[0])
        for i in reversed(range(obj.region.x2, grid_width)):  # Start from current position to right edge
            # Check if all rows in the object's height range have space
            all_rows_clear = True
            for y in range(obj.region.y1, obj.region.y2 + 1):
                if right_side_grid[y][i] != right_side_grid.background_color:
                    all_rows_clear = False
                    break
            
            if all_rows_clear:
                right_side_grid.remove_object(obj)
                right_side_grid = move_object(obj, (i - obj.region.x2), 0, right_side_grid)
                break
    # merge left with right
    for i in range(len(left_side_grid)):
        for j in range(len(left_side_grid[0])):
            if left_side_grid[i][j] != left_side_grid.background_color:
                right_side_grid[i][j] = left_side_grid[i][j]
    return right_side_grid

def rotate_grid(grid: Grid) -> SubGrid:
    """
    Rotate a grid 90 degrees clockwise.
    
    Args:
        grid: The grid to rotate
        
    Returns:
        Grid: The rotated grid
    """
    rows = len(grid)
    cols = len(grid[0])
    new_grid = [[grid[rows-1-j][i] for j in range(rows)] for i in range(cols)]
    return SubGrid(GridRegion([GridPoint(0, 0), GridPoint(rows-1, cols-1)]), Grid(new_grid))

def fit_piece(grid: Grid, piece: Grid, remaining_pieces: Sequence[Grid]) -> Grid:
    """
    Try to fit a piece into a grid at the first valid position, trying different rotations.
    Prevents creating holes smaller than other pieces.
    
    Args:
        grid: The base grid to fit the piece into
        piece: The piece to fit
        remaining_pieces: List of remaining pieces to check against for hole size
        
    Returns:
        Grid: The grid with the piece fitted at the first valid position
    """
    # Try all 4 possible rotations
    original_piece = piece.copy()
    for y in range(len(grid)):
        for x in range(len(grid[0])):
            # Check if we can place the piece at this position
            can_place = True
            # First check if the piece would go out of bounds
            if y + len(piece) > len(grid) or x + len(piece[0]) > len(grid[0]):
                continue
                
            # Then check for overlap with existing pieces
            for py in range(len(piece)):
                for px in range(len(piece[0])):
                    if piece[py][px] != grid.background_color:
                        if grid[y + py][x + px] != grid.background_color:
                            can_place = False
                            break
                if not can_place:
                    break
            
            if can_place:
                # Create a copy of the grid and place the piece
                new_grid = grid.copy()
                for py in range(len(piece)):
                    for px in range(len(piece[0])):
                        if piece[py][px] != new_grid.background_color:
                            new_grid[y + py][x + px] = piece[py][px]
                
                if 0:
                    # Check if this creates any holes smaller than remaining pieces
                    # Get all objects in the new grid
                    objects = detect_objects(new_grid, invert=True)
                    # Get the size of the smallest remaining piece (count non-background values)
                    min_piece_size = float('inf')
                    for p in remaining_pieces:
                        dot_counts = list(p.get_values_count(all=True).values())[0] 
                        if dot_counts < min_piece_size:
                            min_piece_size = dot_counts
                            min_piece = p

                    
                    # Check each object to see if it's a hole (background color)
                    for obj in objects:
                        hole_count = obj.get_values_count(all=True)[new_grid.background_color]
                        if obj.n_rows < min_piece.n_rows or obj.n_cols < min_piece.n_cols or hole_count < min_piece_size:
                            can_place = False
                            breakpoint()
                            break
                
                # check if any piece can fit the border with small space
                if can_place and remaining_pieces and 0:
                    # Check if there are any small spaces at the border that could be filled
                    border_spaces = []
                    # Check top and bottom borders
                    for x in range(len(new_grid[0])):
                        if new_grid[0][x] == new_grid.background_color:
                            border_spaces.append((0, x))
                        if new_grid[-1][x] == new_grid.background_color:
                            border_spaces.append((len(new_grid)-1, x))
                    # Check left and right borders
                    for y in range(len(new_grid)):
                        if new_grid[y][0] == new_grid.background_color:
                            border_spaces.append((y, 0))
                        if new_grid[y][-1] == new_grid.background_color:
                            border_spaces.append((y, len(new_grid[0])-1))
                    
                    # If there are border spaces, check if any remaining piece can fit
                    if border_spaces:
                        for space in border_spaces:
                            space_filled = False
                            for p in remaining_pieces:
                                # Try to fit the piece at this border space
                                if p.n_rows <= 2 and p.n_cols <= 2:  # Only consider small pieces
                                    for py in range(len(p)):
                                        for px in range(len(p[0])):
                                            if p[py][px] != new_grid.background_color:
                                                target_y = space[0] - py
                                                target_x = space[1] - px
                                                if (0 <= target_y < len(new_grid) and 
                                                    0 <= target_x < len(new_grid[0])):
                                                    can_fit = True
                                                    for dy in range(len(p)):
                                                        for dx in range(len(p[0])):
                                                            if p[dy][dx] != new_grid.background_color:
                                                                if new_grid[target_y + dy][target_x + dx] != new_grid.background_color:
                                                                    can_fit = False
                                                                    break
                                                        if not can_fit:
                                                            break
                                                    if can_fit:
                                                        space_filled = True
                                                        break
                                        if space_filled:
                                            break
                            if not space_filled:
                                can_place = False
                                break
                    
                if can_place:
                    return new_grid
    return grid



def remove_pngs():
    for file in glob('*.png'):
        os.remove(file)

remove_pngs()
def jigsaw_recursive(grid: Grid, pieces: list[SubGrid]) -> Grid | None:
    """
    Recursively fit jigsaw puzzle pieces together.
    
    Args:
        first_piece: The current base piece to fit other pieces against
        remaining_pieces: List of Grid objects representing remaining puzzle pieces
        
    Returns:
        Grid: The complete puzzle grid with all pieces fitted together
    """
    # Base case: if no remaining pieces, return the current piece
    global show_count
    if not pieces:
        return grid
    
    # Try to fit each remaining piece
    try:
        pieces.sort(key=lambda x: list(x.get_values_count().values())[0], reverse=True)
    except Exception as e:
        breakpoint()
        
    for piece in pieces:
        grid = grid.copy()
        # Store original piece for rotation attempts
        original_piece = piece.copy()
        # Try all 4 rotations of the piece
        for _ in range(4):
            # Try to fit the piece
            remaining_pieces = [p for p in pieces if p != original_piece]
            new_grid = fit_piece(grid, piece, pieces)
            if new_grid != grid:  # If piece was successfully fitted
                show_count += 1
                print(f"show_count: {show_count}")
                if show_count and 0:
                    plot_grids([new_grid, *remaining_pieces], name=f"grid_{show_count}.png", show=0)
                # Create new list of remaining pieces, excluding the original piece
                # Recursively try to fit remaining pieces
                result = jigsaw_recursive(new_grid, remaining_pieces)
                if result is not None:
                    return result
            piece = rotate_grid(piece)

    return None

def jigsaw_puzzle(grid: Grid) -> Grid:
    """
    Solve a jigsaw puzzle by fitting pieces together.
    
    Args:
        grid: The input grid containing puzzle pieces
        
    Returns:
        Grid: The solved puzzle grid
    """
    global show_count
    show_count = 0  # Reset show count
    start_time = datetime.now()
    # find color map box
    output_grid_size = int(sum(grid.get_values_count().values())**0.5)
    objects = detect_objects(grid)
    print(f"Found {len(objects)} objects")
    
    background_color = grid.background_color
    key_object = None
    first_object = None
    for obj in objects:
        colors = list(obj.get_values_count().keys())
        if len(colors) != 1:
            key_object = obj.copy()
            objects.remove(obj)
            first_object = obj
            # plot_grid(key_object, name="key_object.png", show=True)
            object_color = colors[0]
            key_object.replace_color(object_color, background_color)
            key_object = detect_objects(key_object.get_full_grid())[0]
            
            for row in range(key_object.region.y1, key_object.region.y2 + 1):
                for col in range(key_object.region.x1, key_object.region.x2 + 1):
                    obj[row-obj.region.y1][col-obj.region.x1] = object_color
            break
    
    if key_object is None:
        print("No key object found")
        return grid
    
    key_object_colors = [key_object[row][col] for row in range(key_object.n_rows) for col in range(key_object.n_cols)]
    key_object_colors = [i for i in key_object_colors if i != background_color]
    
    # Create list of puzzle pieces
    # Create empty grid with output_grid_size
    empty_grid = Grid([[background_color] * output_grid_size for _ in range(output_grid_size)])
    
    # Try to solve the puzzle starting with the first piece
    if first_object is not None:
        new_grid = jigsaw_recursive(empty_grid, [first_object])
        if not new_grid:
            print("No new grid found")
        if new_grid is not None:
            result = jigsaw_recursive(new_grid, objects)
            if result is not None:
                for i, color in enumerate(squash_grid(result, background_color)):
                    result.replace_color(color, key_object_colors[i])
                return result
    
    print("No solution found")
    print(f"Time taken: {datetime.now() - start_time}")
    return grid

def row_col_color_data(grid: Grid) -> Grid:
    """
    Create a new grid with row, col, and color data.

    Args:
        divide the grid into 4 subgrids and return the new grid with row, col, and background color (ratio map), data.
        
    """
    grid_size = len(grid)
    subgrid_size = grid_size//2
    # plot_grid(grid, name="input.png", show=True)
    first_piece =  SubGrid(GridRegion([GridPoint(0, 0), GridPoint(subgrid_size-1, subgrid_size-1)]), grid)
    second_piece = SubGrid(GridRegion([GridPoint(subgrid_size, 0), GridPoint(2*subgrid_size-1, subgrid_size-1)]), grid)
    third_piece =  SubGrid(GridRegion([GridPoint(0, subgrid_size), GridPoint(subgrid_size-1, 2*subgrid_size-1)]), grid)
    fourth_piece = SubGrid(GridRegion([GridPoint(subgrid_size, subgrid_size), GridPoint(2*subgrid_size-1, 2*subgrid_size-1)]), grid)
    rows = first_piece.get_total_n_values()
    cols = second_piece.get_total_n_values()
    # breakpoint()
    print(f"rows: {rows}, cols: {cols}")
    # breakpoint()
    new_grid = []
    row_ratio = rows//subgrid_size or 1
    col_ratio = cols//subgrid_size or 1
    for row in range(rows):
        new_row = []
        for col in range(cols):
            row_idx = row % subgrid_size
            col_idx = col % subgrid_size
            new_val = fourth_piece[row_idx][col_idx]
            if not new_val:
                new_val = third_piece[(row//row_ratio)%subgrid_size][(col//col_ratio)%subgrid_size]
            new_row.append(new_val)
        new_grid.append(new_row)
    return new_grid




if 1:
    normal_task_fns = [
            count_hollows_task,
            check_fit,
            move_object_without_collision,
            repeat_reverse_grid,
        ]
else:
    normal_task_fns = [row_col_color_data]

jigsaw_task_fns = [
    # jigsaw_puzzle,
    row_col_color_data, # can occur in normal task
]



def debug_output(grid, expected_output, output):
    print('Debugging output')
    # print which cells are different
    for i in range(len(expected_output)):
        for j in range(len(expected_output[0])):
            if expected_output[i][j] != output[i][j]:
                print(f"Cell {i}, {j} is different")
    plot_grids([grid, expected_output, output],)
    breakpoint()

def find_task(grids, expected_outputs):
    if len(grids[0][0]) == len(expected_outputs[0][0]):
        task_fns = normal_task_fns
    else:
        task_fns = jigsaw_task_fns
    for task_fn in task_fns:
        print(task_fn.__name__)
        right_task = True
        for grid, expected_output in zip(grids, expected_outputs):
            grid = Grid(grid)
            expected_output = Grid(expected_output)
            plot_grid(expected_output, name="expected_output.png")
            plot_grid(grid, name="input.png")
            output = task_fn(grid)
            plot_grid(output, name="actual_output.png")
            if output != expected_output:
                # debug_output(grid, expected_output, output)
                right_task = False
                break
        if right_task:
            return task_fn
        print('--------------------------------')
    return None

def solve_task(data):
    num_train_tasks = len(data['train'])
    num_test_tasks = len(data['test'])
    print(f"Number of train tasks: {num_train_tasks}, Number of test tasks: {num_test_tasks}")
    start_train_task_id = 0
    start_test_task_id = 0
    actual_task_name = None
    # start_train_task_id = 3
    # start_test_task_id = 0
    # actual_task_name = row_col_color_data
    grids = []
    expected_outputs = []
    actual_outputs = []
    if not actual_task_name:
        for task_id in range(start_train_task_id, num_train_tasks):
            grids.append(data['train'][task_id]['input'])
            expected_outputs.append(data['train'][task_id]['output'])
        task_fn = find_task(grids, expected_outputs)
        if not task_fn:
            print(f"Task not found")
    else:
        task_fn = actual_task_name
    for task_id in range(start_test_task_id, num_test_tasks):
        grid = Grid(data['test'][task_id]['input'])
        if task_fn:
            plot_grid(grid, name="input.png")
            expected_output = Grid(data['test'][task_id].get('output'))
            plot_grid(expected_output, name="expected_output.png")
            print(f"Found task: {task_fn.__name__}")
            output = task_fn(grid)
            plot_grid(output, name="actual_output.png")
            if expected_output:
                if output == expected_output:
                    print(f"Correct: {task_fn.__name__}")
                else:
                    raise Exception(f"Incorrect: {task_fn.__name__}, Expected: {expected_output}, Actual: {output}")
            output = {"attempt_1": output, "attempt_2": output}
        else:
            output = {"attempt_1": grid, "attempt_2": grid}
        actual_outputs.append(output)
    return actual_outputs

if __name__ == "__main__":
    files = glob('C:/Users/smart/Desktop/GD/ARC-AGI-2/data/evaluation/*.json')
    file = files[14]
    # print(file)
    # file = r'C:/Users/smart/Desktop/GD/ARC-AGI-2/data/evaluation/e3721c99.json'
    # file = r'C:/Users/smart/Desktop/GD/ARC-AGI-2/data/evaluation/cbebaa4b.json'
    # file = r'C:/Users/smart/Desktop/GD/ARC-AGI-2/data/evaluation/b5ca7ac4.json'
    file = r'C:/Users/smart/Desktop/GD/ARC-AGI-2/data/evaluation/f560132c.json'
    file = r'C:/Users/smart/Desktop/GD/ARC-AGI-2/data/evaluation/f931b4a8.json'
    # file = r'C:/Users/smart/Desktop/GD/ARC-AGI-2/data/training/00576224.json'
    data = json.load(open(file, 'r'))
    from pprint import pprint
    solve_task(data)
