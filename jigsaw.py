from typing import Sequence
from arc_tools.grid import Grid, SubGrid, GridRegion, GridPoint, detect_objects


from datetime import datetime

from arc_tools.plot import plot_grids
from arc_tools.squash import squash_grid

show_count = 0
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

