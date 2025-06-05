from collections import Counter
from arc_tools import grid
from arc_tools.grid import Grid, detect_objects, Color, SubGrid, GridRegion, GridPoint, move_object, Square
from arc_tools.plot import plot_grid, plot_grids
from arc_tools.logger import logger

def just_walk(grid: Grid) -> Grid:
    '''
    background color != first dot color
    top left 2x2 objects - dots color sequence
    bottom right 2x2 object - dot color of next collided dot
    walk direction - right, up  repeat
    '''
    # Detect top left objects (color sequence)
    # replace max color object with background color
    max_color = grid.get_max_color()
    if max_color != grid[0][0]:
        max_color, grid.background_color = grid.background_color, max_color
    clean_grid = grid.copy()
    clean_grid.replace_color(max_color, clean_grid.background_color)
    knowledge_boxes = detect_objects(clean_grid, required_object=Square(2))
    *top_left_objs, bottom_right_obj = knowledge_boxes
    for obj in knowledge_boxes:
        grid.remove_object(obj, max_color)
    color_sequence = [obj[0][0] for obj in top_left_objs]
    color_sequence_length = len(color_sequence)
    collision_color = bottom_right_obj[0][0]
    dots = [x for x in detect_objects(clean_grid) if x.region.width == 1 and x.region.height == 1]
    for dot in dots:
        idx = 1
        cur_x, cur_y = dot.region.x1, dot.region.y1
        direction = 0  # 0: right, 1: up
        for _ in range(5):
            if direction == 0:  # move right
                first_move = True
                while cur_x + 1 < grid.width and grid[cur_y][cur_x + 1] == grid.background_color:
                    cur_x += 1
                    if first_move and grid[cur_y][cur_x] != grid.background_color:
                        break
                    first_move = False
                    grid[cur_y][cur_x] = color_sequence[idx % color_sequence_length]
                    idx += 1
                # collision or edge
                if not first_move and cur_x + 1 < grid.width and grid[cur_y][cur_x + 1] != grid.background_color:
                    grid[cur_y][cur_x + 1] = collision_color
                else:
                    break
            else:  # move up
                first_move = True
                while cur_y - 1 >= 0 and grid[cur_y - 1][cur_x] == grid.background_color:
                    cur_y -= 1
                    if first_move and grid[cur_y][cur_x] != grid.background_color:
                        break
                    first_move = False
                    grid[cur_y][cur_x] = color_sequence[idx % color_sequence_length]
                    idx += 1
                # collision or edge
                if not first_move and cur_y - 1 >= 0 and grid[cur_y - 1][cur_x] != grid.background_color:
                    grid[cur_y - 1][cur_x] = collision_color
                else:
                    break
            direction = 1 - direction  # alternate direction
    return grid

if __name__ == "__main__":
    import os
    os.system("python main.py 195c6913 just_walk")