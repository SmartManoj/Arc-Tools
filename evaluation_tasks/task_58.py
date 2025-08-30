from typing import Sequence
from arc_tools.grid import Color, Grid, SubGrid, detect_objects


from datetime import datetime

from arc_tools.plot import plot_grids

show_count = 0

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
                        if obj.height < min_piece.height or obj.width < min_piece.width or hole_count < min_piece_size:
                            can_place = False
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
                                if p.height <= 2 and p.width <= 2:  # Only consider small pieces
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
        
    Returns:
        Grid: The complete puzzle grid with all pieces fitted together
    """
    # Base case: if no remaining pieces, return the current piece
    global show_count
    if not pieces:
        return grid
    
    # Try to fit each remaining piece
    pieces.sort(key=lambda x: list(x.get_values_count().values())[0], reverse=True)
        
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
                # print(f"show_count: {show_count}")
                if show_count and 0:
                    plot_grids([new_grid, *remaining_pieces], name=f"grid_{show_count}.png", show=0)
                # Create new list of remaining pieces, excluding the original piece
                # Recursively try to fit remaining pieces
                result = jigsaw_recursive(new_grid, remaining_pieces)
                if result is not None:
                    return result
            piece = piece.rotate()

    return None

def jigsaw_v1(grid: Grid) -> Grid:
    """
    find output grid size by counting the number of objects in the input grid
    1. find color map box
    2. piece that having the color map box is the first piece without rotation.
    3. move the jigsaw puzzle pieces to the correct position (do largest piece first)
    4. replace colors of the objects in the output grid with the color map
    """
    global show_count
    show_count = 0  # Reset show count
    start_time = datetime.now()
    # find color map box
    output_grid_size = int(sum(grid.get_values_count().values())**0.5)
    objects = detect_objects(grid)
    
    background_color = grid.background_color
    key_object = None
    first_object = None
    for obj in objects:
        if obj.color is None:
            objects.remove(obj)
            for _ in range(4):
                if obj[0][0] == Color.LIGHT_GRAY.value:
                    first_object = obj
                    break
                obj = obj.rotate()
            break
    
    
    
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
                return result
    
    return grid

if __name__ == "__main__":
    import os
    os.system("main.py 7b3084d4 jigsaw_v1")


