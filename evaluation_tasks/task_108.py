from itertools import product
import os
from arc_tools.grid import BorderSide, Grid, detect_objects, Color
from arc_tools import logger
from arc_tools.plot import plot_grids


def fill_the_gap(grid: Grid):
    '''
    Remove extra single dots
    Remove gaps and replace them with light blue cells surrounded by 3x3 boxes.
    '''
    original_grid = grid.copy()
    grid.background_color = Color.BLACK.value
    
    all_objects = detect_objects(grid, single_color_only=1)
    objects = []
    for obj in all_objects:
        if obj.area == 1:
            grid.remove_object(obj)
        else:
            objects.append(obj)
    for obj in objects:
        for side in BorderSide:
            edge_points = [p for p in obj.get_edge_points(side)]
            valid_edge_points = [p for p in edge_points if p.value == obj.color]
            if len(edge_points) - len(valid_edge_points) <= 2: # for train task
                continue
            for idx, point in enumerate(edge_points):
                if point.value == obj.color and edge_points[idx - 1].value != point.value != edge_points[idx + 1].value:
                    sp_values = [c.value for c in grid.get_surrounding_points(point.y, point.x) if c.value != obj.color]
                    grid[point.y][point.x] = sp_values[0] if sp_values else grid.background_color
    for row, col in grid.all_points:
        sp_values = [p.value for p in grid.get_surrounding_points(row, col)]
        other_colors = list(set(c for c in sp_values if c != grid[row][col]))
        if len(sp_values) == 8 and sp_values.count(grid[row][col]) == 3 and len(other_colors)== 1:
            if (
                sp_values[0] == sp_values[1] == sp_values[2] == grid[row][col] or # left
                sp_values[0] == sp_values[3] == sp_values[5] == grid[row][col] or # top
                sp_values[5] == sp_values[6] == sp_values[7] == grid[row][col] or # right
                sp_values[2] == sp_values[4] == sp_values[7] == grid[row][col] # bottom
                ):
                grid[row][col] = other_colors[0]

    objects = detect_objects(grid, single_color_only=1)    
    # plot_grids(objects)
    all_colors = list(set(obj.color for obj in objects))
    for idx, obj in enumerate(objects):
        blue_positions = []
        for row, col in product(range(obj.region.start.y, obj.region.end.y + 1), range(obj.region.start.x, obj.region.end.x + 1)):
            if grid[row][col] == Color.BLACK.value and obj.color in [c.value for c in grid.get_surrounding_points(row, col)]:
                grid[row][col] = Color.LIGHT_BLUE.value
                blue_positions.append((row, col))
        
        # Create 3x3 box around each light blue cell
        box_color = [c for c in all_colors if c != obj.color][0]
        for row, col in blue_positions:
            for r in range(-1, 2):
                for c in range(-1, 2):
                    if 0 <= row + r < grid.height and 0 <= col + c < grid.width:
                        # Only fill if the cell is not light blue
                        if grid[row + r][col + c] != Color.LIGHT_BLUE.value:
                            grid[row + r][col + c] = box_color
        # plot_grids([grid])
    return grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py de809cff fill_the_gap") 
