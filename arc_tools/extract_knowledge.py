

def extract_knowledge_vertically(grid):
    # Find the column where all elements are 1
    split_col = None
    for col in range(len(grid[0])):  # Iterate over each column
        if all(row[col] == 1 for row in grid):  # Check if all rows have 1 in this column
            split_col = col
            break

    if split_col is not None:
        left_part = [row[:split_col] for row in grid]  # All columns before split_col
        right_part = [row[split_col+1:] for row in grid]  # All columns after split_col
        if len(left_part[0]) > len(right_part[0]):
            return right_part
        else:
            return left_part

def extract_knowledge_horizontally(grid):
    split_row = None
    for i in range(len(grid)):
        if all(grid[i][j] == 1 for j in range(len(grid[0]))):  # Check if row has at least one 1
            # Check if this row is different from the previous pattern
            if i > 0 and any(grid[i][j] != grid[i-1][j] for j in range(len(grid[0]))):
                split_row = i
                break
    if split_row:
        top_part = grid[:split_row]
        bottom_part = grid[split_row+1:]
        if len(top_part) > len(bottom_part):
            return bottom_part
        else:
            return top_part



def extract_knowledge_lshape(grid): # Keep the signature
    # Don't change the function signature
    # Don't use global variables or identity checks

    num_rows = len(grid)
    # Basic validation for grid structure
    if num_rows == 0 or len(grid[0]) == 0:
        return []

    # Determine num_cols based on the index of the first '1' in the first row
    num_cols = 3 # Default if '1' is not found, matching original slice [:3]
    try:
        first_row = grid[0]
        num_cols = first_row.index(1)
    except ValueError:
        # '1' not found in the first row, keep default num_cols = 3
        pass
    except IndexError:
         # Should not happen if rows > 0 check passed, but handle defensively
         return []


    if num_rows < 2:
        # If only 1 row, return the slice of that row based on num_cols
        row = grid[0]
        actual_cols = min(num_cols, len(row))
        return [row[:actual_cols]] # Return as a list containing one row

    l_shape = []
    # Extract first min(2, rows) rows, and num_cols columns
    for i in range(num_rows):
        row = grid[i]
        # Ensure we don't try to slice beyond the actual row length
        actual_cols = min(num_cols, len(row))
        new_row = row[:actual_cols]
        if all(x == 1 for x in new_row):
            break
        l_shape.append(new_row)
    return l_shape

def extract_knowledge(grid):
    split = extract_knowledge_vertically(grid)
    if not split:
        split = extract_knowledge_horizontally(grid)
    if not split:
        split = extract_knowledge_lshape(grid)
    if not split:
        split = grid
    return split

if __name__ == "__main__":
        
    a1 = [
        [1, 2, 1, 3],
        [0, 0, 1, 0],
        [0, 0, 1, 0],
        [0, 0, 1, 0]
    ]

    # transpose a
    a2 = list(zip(*a1))
    print(extract_knowledge_horizontally(a2))
