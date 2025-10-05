import os
from arc_tools.grid import Grid, detect_objects, Color
from arc_tools import logger
from arc_tools.plot import plot_grids

def remove_specific_objects(grid: Grid):
    '''
    remove black objects that contains all hint obj colors
    '''
    grid.background_color = Color.ORANGE.value
    objects = detect_objects(grid, ignore_colors= [Color.GREEN])
    black_objects = []
    hint_colors = []
    for obj in objects:
        if Color.BLACK.value in obj.colors:
            black_objects.append(obj)
        else:
            hint_colors.extend(obj.colors)
    for obj in black_objects:
        if all(color in obj.colors for color in hint_colors):
            grid.remove_object(obj)
    return grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py d59b0160 remove_specific_objects") 
