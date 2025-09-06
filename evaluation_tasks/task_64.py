import os
from arc_tools.grid import BorderSide, Grid, GridPoint, detect_objects
from arc_tools import logger
from arc_tools.plot import plot_grids

def draw_diagonal(gp: GridPoint, direction: str, grid: Grid):
    if direction == "top-left":
        x, y = gp.x - 1, gp.y - 1
        while x >= 0 and y >= 0:
            grid.set(x, y, gp.value)
            x -= 1
            y -= 1
    elif direction == "bottom-right":
        x, y = gp.x + 1, gp.y + 1
        while x < grid.width and y < grid.height:
            grid.set(x, y, gp.value)
            x += 1
            y += 1
    elif direction == "top-right":
        x, y = gp.x + 1, gp.y - 1
        while x < grid.width and y >= 0:
            grid.set(x, y, gp.value)
            x += 1
            y -= 1
    elif direction == "bottom-left":
        x, y = gp.x - 1, gp.y + 1
        while x >= 0 and y < grid.height:
            grid.set(x, y, gp.value)
            x -= 1
            y += 1

def pathways(grid: Grid):
    '''
    Simple approach: Find object edges with 3 colors, extend from the two corners 
    of that edge in perpendicular direction.
    '''
    grid.background_color = 0
    
    # Find all colored objects (non-background, non-alternating pattern colors)
    objects = detect_objects(grid, ignore_color=1)
    for obj in objects:
        # plot_grids([grid,obj])
        # Get all colored points in the object
        
        top_row = obj.get_edge_data(BorderSide.TOP)
        ignore_colors = [0, 1]
        for cell in top_row:
            if cell.value not in ignore_colors:
                is_anti_diagonal = grid.get(cell.x - 1, cell.y + 1) != cell.value
                is_main_diagonal = grid.get(cell.x + 1, cell.y + 1) != cell.value
                if is_anti_diagonal:
                    draw_diagonal(cell, "top-right", grid)
                elif is_main_diagonal:
                    draw_diagonal(cell, "top-left", grid)
        left_row = obj.get_edge_data(BorderSide.LEFT)
        for cell in left_row:
            if cell.value not in ignore_colors:
                is_anti_diagonal = grid.get(cell.x + 1, cell.y - 1) != cell.value
                is_main_diagonal = grid.get(cell.x + 1, cell.y + 1) != cell.value
                if is_anti_diagonal:
                    draw_diagonal(cell, "bottom-left", grid)
                elif is_main_diagonal:
                    draw_diagonal(cell, "top-left", grid)
        bottom_row = obj.get_edge_data(BorderSide.BOTTOM)
        for cell in bottom_row:
            if cell.value not in ignore_colors:
                is_anti_diagonal = grid.get(cell.x + 1, cell.y - 1) != cell.value
                is_main_diagonal = grid.get(cell.x + 1, cell.y + 1) != cell.value
                if is_anti_diagonal:
                    draw_diagonal(cell, "bottom-left", grid)
                elif is_main_diagonal:
                    draw_diagonal(cell, "bottom-right", grid)
        right_row = obj.get_edge_data(BorderSide.RIGHT)
        for cell in right_row:
            if cell.value not in ignore_colors:
                is_anti_diagonal = grid.get(cell.x - 1, cell.y + 1) != cell.value
                is_main_diagonal = grid.get(cell.x + 1, cell.y + 1) != cell.value
                if is_anti_diagonal:
                    draw_diagonal(cell, "top-right", grid)
                elif is_main_diagonal:
                    draw_diagonal(cell, "bottom-right", grid)
    return grid

def get_nearest_color(x, y, color_groups):
    """Find the nearest color to the given position"""
    min_dist = float('inf')
    nearest_color = 2  # default color
    
    for color, positions in color_groups.items():
        for pos_x, pos_y in positions:
            dist = abs(x - pos_x) + abs(y - pos_y)  # Manhattan distance
            if dist < min_dist:
                min_dist = dist
                nearest_color = color
    
    return nearest_color

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 80a900e0 pathways")