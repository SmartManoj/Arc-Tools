import os

from numpy import var
from arc_tools import plot
from arc_tools.grid import Grid, detect_objects, place_object, place_object_on_new_grid
from arc_tools import logger
from arc_tools.plot import plot_grids

def enlarge_and_fit(grid: Grid):
    '''
    Enlarge the frame and fit the objects by rotating it if needed.
    '''
   
    # Detect objects first
    objects = detect_objects(grid)
    # sort it
    objects = sorted(objects, key=lambda obj: obj.area, reverse=True)
    # frame is the largest object
    frame = objects.pop(0)


    noise_obj_color = objects[-1].color
    objects = [obj for obj in objects if obj.color != noise_obj_color]

    frame = Grid(frame).enlarge(objects[-1].width)

    objects = [obj.replace_color(noise_obj_color, grid.background_color, replace_in_parent_grid=0) for obj in objects]


    holes = detect_objects(frame)
    frame.background_color = grid.background_color
    placed_objects = []
    for hole in holes:
        for idx, obj in enumerate(objects):
            if idx in placed_objects: continue
            placed = False
            # Try all rotations and flips
            for variation in range(8):
                if hole.is_similar(obj, ignore_color=True, rotate=False):
                    place_object_on_new_grid(obj, hole.region.x1, hole.region.y1, frame)
                    placed = True
                    placed_objects.append(idx)
                    break
                if variation == 4:
                        obj = obj.flip_horizontally()
                obj = obj.rotate()
            if placed: break
        else:
            plot_grids([frame, hole, obj])
    return frame

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 898e7135 enlarge_and_fit") 
