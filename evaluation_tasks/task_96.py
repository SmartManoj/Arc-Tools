import os
from arc_tools.grid import Grid, detect_objects, Color
from arc_tools import logger
from arc_tools.plot import plot_grids


def complete_pattern(current_pattern, expected_pattern):
    """Find which rows match the input and return dx,dy offsets from matching row's first column to other elements."""
    input_arr = current_pattern[0]  # Extract the row from nested list

    # Find matching rows
    matching_rows = []
    for i, row in enumerate(expected_pattern):
        for col_slice in range(len(row)):
            if row[col_slice:col_slice + len(input_arr)] == input_arr:
                matching_rows.append((i, col_slice))
                break


    anchor_pos = matching_rows[0]


    offsets = []
    for row in range(len(expected_pattern)):
        for col in range(len(expected_pattern[row])):
            if (row, col) != anchor_pos:
                dx = col - anchor_pos[1]
                dy = row - anchor_pos[0]
                offsets.append((dx, dy))

    return anchor_pos, offsets

def cult_v2(grid: Grid):
    '''
    single dots - expected pattern
    copy the pattern to the other objects
    '''
    full_objects = detect_objects(grid)
    single_dots = []
    objects = []
    for obj in full_objects:
        if obj.width == 1:
            single_dots.append(obj)
        else:
            objects.append(obj)
    
    # generate expected pattern
    expected_patten = [[single_dots[0]]]
    for dot in single_dots[1:]:
        if dot.region.y1 == expected_patten[-1][-1].region.y1:
            expected_patten[-1].append(dot)
        else:
            expected_patten.append([dot])
    
    # change to dot color
    expected_patten = [[dot.color for dot in row] for row in expected_patten]
    current_pattern = [[objects[0].color, objects[1].color]]

    anchor_pos, offsets = complete_pattern(current_pattern, expected_patten)
    anchor_object = objects[0]
    step = objects[1].region.x1 - anchor_object.region.x2 - 1
    for dx, dy in offsets:
        for row in range(anchor_object.region.y1, anchor_object.region.y2+1):
            for col in range(anchor_object.region.x1, anchor_object.region.x2+1):
                grid[row + step * dy + dy * anchor_object.height][col + step * dx + dx * anchor_object.width] = expected_patten[dy + anchor_pos[0]][dx + anchor_pos[1]]


    return grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py c4d067a0 cult_v2") 
