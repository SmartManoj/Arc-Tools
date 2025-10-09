import os
from arc_tools.grid import Grid, detect_objects, Color, place_object_on_new_grid
from arc_tools import logger
from arc_tools.plot import plot_grids

def dot_com_bubble(grid: Grid):
    '''
    each dot color is replaced by certain objects
    if a dot is attached by another object, it will be removed and used.
    '''
    # Default patterns for dots when no attached object is found
    yellow_square = [
        [4, 4, 4, 4],
        [4, 0, 0, 4],
        [4, 0, 0, 4],
        [4, 4, 4, 4],
    ]
    
    blue_diamond = [
        [0, 1, 1, 0],
        [1, 0, 0, 1],
        [1, 0, 0, 1],
        [0, 1, 1, 0],
    ]
    orange_cross = [
        [7, 0, 0, 7],
        [0, 7, 7, 0],
        [0, 7, 7, 0],
        [7, 0, 0, 7],
    ]
    magenta_box = [
        [6, 6, 0, 0],
        [6, 6, 0, 0],
        [0, 0, 6, 6],
        [0, 0, 6, 6],
    ]
    objects = detect_objects(grid, single_color_only=True)
    dots = []
    key_object = None
    for obj in objects:
        if obj.region.width == 1 and obj.region.height == 1:
            dots.append(obj)
        else:
            key_object = obj
    

    
    dot_patterns = {
        Color.RED.value: Grid(yellow_square, background_color=grid.background_color),
        Color.GREEN.value: Grid(blue_diamond, background_color=grid.background_color),
        Color.LIGHT_BLUE.value: Grid(orange_cross, background_color=grid.background_color),
        Color.GRAY.value: Grid(magenta_box, background_color=grid.background_color),
    }
    if key_object:
        key_color : int = grid[key_object.region.y2 + 1][key_object.region.x2 + 1] # pyright: ignore
        dot_patterns[key_color] = key_object
        grid.replace_color(key_object.color, grid.background_color)

    for dot in dots:
        grid.remove_object(dot)
        if key_object:
            if dot.region.x1 == key_object.region.x2 + 1 and dot.region.y1 == key_object.region.y2 + 1:
                continue
        pattern = dot_patterns[dot.color]
        place_object_on_new_grid(pattern, dot.region.x1, dot.region.y1, grid)
    
    return grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py dfadab01 dot_com_bubble") 
