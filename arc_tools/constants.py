# clockwise: right, down, left, up
CARDINAL_DIRECTIONS = [(1, 0), (0, -1), (-1, 0), (0, 1)]
# clockwise: right-up, right-down, left-down, left-up
ORDINAL_DIRECTIONS = [(1, -1), (1, 1), (-1, -1), (-1, 1)]
# clockwise: right-up, right, right-down, down, down-left, left, left-up, up
EIGHT_DIRECTIONS = []
for i in range(4):
    EIGHT_DIRECTIONS.append(CARDINAL_DIRECTIONS[i])
    EIGHT_DIRECTIONS.append(ORDINAL_DIRECTIONS[i])
