import os
from arc_tools.grid import Grid, detect_objects, SubGrid, Color
from arc_tools import logger
from arc_tools.plot import plot_grids
from collections import Counter

def majority(grid: Grid):
    '''
    Transform a 30x30 grid into an 11x11 grid with yellow background.
    Extract objects from the input grid and place them in a compressed format.
    '''
    objects = detect_objects(grid, single_color_only=1)
    frame_color = grid.get_max_color()
    for object in objects:
        if object.get_max_color() == frame_color:
            objects.remove(object)
            frame_grid = Grid(object)
            break
    # remove frame_obj from objects
    # convert all as grid
    new_objects = []
    for object in objects:
        obj = Grid(object, grid.background_color).as_sub_grid()
        if obj.height > obj.width:
            obj = obj.rotate()
        new_objects.append(obj)
        
    # Counter by resemblance
    counter = Counter(new_objects)
    # rotate and compare
    counter_list = list(i[0] for i in counter.most_common())
    frame_objects = detect_objects(frame_grid)
    for frame_object in frame_objects:
        for object in counter_list:
            if frame_object.is_similar(object, ignore_color=True):
                frame_object.replace_color(Color(frame_object.color), Color(object.color))
                break
        else:
            logger.info(f"No similar object found for {frame_object}")
            # plot_grids([frame_object, *counter_list])
    return frame_grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 67e490f4 majority") 
