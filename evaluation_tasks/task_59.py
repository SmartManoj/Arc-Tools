import os
from arc_tools.grid import Grid, detect_objects

def straight_snake(grid: Grid):
    '''
    vertically align the points
    '''
    object = detect_objects(grid)[0]
    return Grid([[grid.get(point.x, point.y)] for point in object.points])

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 7b5033c1 straight_snake") 
