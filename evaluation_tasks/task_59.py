import os
from arc_tools.grid import Grid, detect_objects
from arc_tools import logger
from arc_tools.plot import plot_grids

def straight_snake(grid: Grid):
    '''
    add the function description first.
    '''
    object = detect_objects(grid)[0]
    # vertically align the points
    straight_snake = []
    for point in object.points:
        straight_snake.append([grid.get(point.x, point.y)])

    
    return Grid(straight_snake)

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 7b5033c1 straight_snake") 
