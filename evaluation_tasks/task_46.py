import os
from collections import Counter
from arc_tools.grid import Grid, detect_objects, move_object

def gravity(grid: Grid):
    '''
    Repeated shapes float, unique shapes sink.
    '''
    objects = detect_objects(grid)
    
    objects_dots_counter = Counter(obj.get_total_dots() for obj in objects)
    for obj in objects:
        if objects_dots_counter[obj.get_total_dots()] > 1:
            move_object(obj, 0, -obj.region.y1, grid)
        else:
            move_object(obj, 0, grid.height - obj.region.y2 - 1, grid)
    
    
    return grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 62593bfd gravity") 
