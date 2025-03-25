

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



def extract_knowledge_lshape(grid):
    # split = extract_knowledge_vertically(a)
    # if not split:
    #     split = extract_knowledge_horizontally(a)
    # if not split:
    #     split = extract_knowledge_lshape(a)
    pass

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
