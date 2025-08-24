import os
from collections import Counter
from arc_tools.grid import Grid, GridPoint, Color

def split_pieces(grid_data, magenta_points):
    """
    Step 1: Split the grid into pieces based on magenta separators
    Returns: pieces (list of grid sections)
    """
    h, w = len(grid_data), len(grid_data[0])
    
    # Check if magenta forms horizontal or vertical separators
    magenta_rows = set(p.y for p in magenta_points)
    magenta_cols = set(p.x for p in magenta_points)
    
    # If magenta spans full width in certain rows, it's horizontal separation
    horizontal_separators = []
    for row in magenta_rows:
        row_magenta_cols = [p.x for p in magenta_points if p.y == row]
        if len(row_magenta_cols) == w:  # Full width
            horizontal_separators.append(row)
    
    # If magenta spans full height in certain columns, it's vertical separation  
    vertical_separators = []
    for col in magenta_cols:
        col_magenta_rows = [p.y for p in magenta_points if p.x == col]
        if len(col_magenta_rows) == h:  # Full height
            vertical_separators.append(col)
    
    # Split based on separator patterns
    quads_dict = None
    final_pieces = None
    
    if horizontal_separators and vertical_separators:
        # Both separators exist - create quad dictionary
        center_y = horizontal_separators[0]
        center_x = vertical_separators[0]
        
        quads_dict = {
            'tl': [row[0:center_x] for row in grid_data[0:center_y]],
            'tr': [row[center_x+1:w] for row in grid_data[0:center_y]],
            'bl': [row[0:center_x] for row in grid_data[center_y+1:h]],
            'br': [row[center_x+1:w] for row in grid_data[center_y+1:h]],
        }
    elif vertical_separators:
        # Vertical separators only
        vertical_separators.sort()
        sections = []
        
        start_col = 0
        for sep_col in vertical_separators:
            if sep_col > start_col:
                sections.append([row[start_col:sep_col] for row in grid_data])
            start_col = sep_col + 1
        
        if start_col < w:
            sections.append([row[start_col:w] for row in grid_data])
        
        final_pieces = sections
        
    elif horizontal_separators:
        # Horizontal separators only
        horizontal_separators.sort()
        sections = []
        
        start_row = 0
        for sep_row in horizontal_separators:
            if sep_row > start_row:
                sections.append([row[:] for row in grid_data[start_row:sep_row]])
            start_row = sep_row + 1
        
        if start_row < h:
            sections.append([row[:] for row in grid_data[start_row:h]])
        
        final_pieces = sections
    
    # Return either quad pieces or section pieces
    if quads_dict is not None:
        return [quads_dict['tl'], quads_dict['tr'], quads_dict['bl'], quads_dict['br']]
    else:
        return final_pieces

def arrange_the_pieces(pieces, bg_color):
    """
    Step 2: Determine the order and orientation for joining pieces  
    Returns: (final_pieces_ordered, join_horizontally)
    """
    # Check if all pieces have clean left and right borders
    def has_clean_left_right_borders(piece, bg_color):
        if not piece or not piece[0]:
            return True
        
        # Check left border (first column)
        left_clean = all(row[0] == bg_color for row in piece if row)
        # Check right border (last column)  
        right_clean = all(row[-1] == bg_color for row in piece if row)
        
        return left_clean and right_clean
    
    # Determine join direction
    all_pieces_clean_lr = all(has_clean_left_right_borders(piece, bg_color) for piece in pieces)
    
    if all_pieces_clean_lr:
        join_horizontally = False  # Vertical join (stack vertically)
    else:
        join_horizontally = True   # Horizontal join (place side by side)
    
    # Find optimal order by matching structures based on join direction
    def get_top_row_structure(piece, bg_color):
        """Get the structure pattern of the top row"""
        if not piece or not piece[0]:
            return []
        return [1 if cell != bg_color else 0 for cell in piece[0]]
    
    def get_bottom_row_structure(piece, bg_color):
        """Get the structure pattern of the bottom row"""
        if not piece:
            return []
        return [1 if cell != bg_color else 0 for cell in piece[-1]]
    
    def get_left_edge_structure(piece, bg_color):
        """Get the structure pattern of the left edge"""
        if not piece:
            return []
        return [1 if row[0] != bg_color else 0 for row in piece if row]
    
    def get_right_edge_structure(piece, bg_color):
        """Get the structure pattern of the right edge"""
        if not piece:
            return []
        return [1 if row[-1] != bg_color else 0 for row in piece if row]
    
    # Find the starting piece: top and left edges should be clean
    def has_clean_top_edge(piece, bg_color):
        if not piece or not piece[0]:
            return True
        return all(cell == bg_color for cell in piece[0])
    
    def has_clean_left_edge(piece, bg_color):
        if not piece:
            return True
        return all(row[0] == bg_color for row in piece if row)
    
    # Find valid starting piece (clean top and left edges)
    for i, piece in enumerate(pieces):
        if has_clean_top_edge(piece, bg_color) and has_clean_left_edge(piece, bg_color):
            start_idx = i
            break
    
    # Build the sequence greedily
    ordered_indices = [start_idx]
    remaining_indices = [i for i in range(len(pieces)) if i != start_idx]
    
    # Greedily add the best matching piece at each step
    while remaining_indices:
        current_piece = pieces[ordered_indices[-1]]
        
        if join_horizontally:
            current_edge = get_right_edge_structure(current_piece, bg_color)
        else:
            current_edge = get_bottom_row_structure(current_piece, bg_color)
        
        for idx in remaining_indices:
            candidate_piece = pieces[idx]
            
            if join_horizontally:
                candidate_edge = get_left_edge_structure(candidate_piece, bg_color)
            else:
                candidate_edge = get_top_row_structure(candidate_piece, bg_color)
            
            if current_edge == candidate_edge:
                ordered_indices.append(idx)
                remaining_indices.remove(idx)
                break
        
    final_pieces_ordered = [pieces[i] for i in ordered_indices]
    
    return final_pieces_ordered, join_horizontally

def join_the_pipes(grid: Grid):
    """
    Joins separated grid sections into a continuous grid.
    
    Step 1: Split pieces based on magenta separators
    Step 2: Determine join direction - if all pieces have clean left/right borders, join vertically
    Step 3: Find starting piece with clean top and left edges
    Step 4: Greedily connect pieces by matching edge structures
    Step 5: Join pieces horizontally or vertically as determined

    Notes:
    - Each section is a 5x5 grid.
    """
    
    grid_data = [list(row) for row in grid]
    bg_color = grid.background_color
    magenta_points = [GridPoint(c, r) for r, row in enumerate(grid_data) for c, val in enumerate(row) if val == Color.MAGENTA.value]
    
    # Step 1: Split the pieces
    pieces = split_pieces(grid_data, magenta_points)
    
    # Step 2: Arrange the pieces - determine order and orientation
    final_pieces_ordered, join_horizontally = arrange_the_pieces( pieces, bg_color)
    
    # Step 3: Join the pieces
    if join_horizontally:
        # Horizontal join - place pieces side by side
        max_height = len(final_pieces_ordered[0])
        
        output_grid_data = []
        for row_idx in range(max_height):
            output_row = []
            for i, piece in enumerate(final_pieces_ordered):
                output_row.extend(piece[row_idx])
                if i < len(final_pieces_ordered) - 1:
                    output_row.append(Color.MAGENTA.value)
            output_grid_data.append(output_row)
    else:
        # Vertical join - place pieces vertically
        max_width = len(final_pieces_ordered[0])
        
        output_grid_data = []
        for i, piece in enumerate(final_pieces_ordered):
            output_grid_data.extend(piece)
            if i < len(final_pieces_ordered) - 1:
                output_grid_data.append([Color.MAGENTA.value] * max_width)

    return Grid(output_grid_data, background_color=bg_color)

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 78332cb0 join_the_pipes")