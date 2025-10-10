import os
from arc_tools.grid import Grid, GridRegion, SubGrid, detect_objects, Color, place_object, GridPoint
from arc_tools import logger
from arc_tools.plot import plot_grid, plot_grids

def fit_it(grid: Grid):
    '''
    fit the objects into the largest frames.
    '''
    objects = detect_objects(grid)
    objects.sort(key=lambda x: x.area, reverse=1)
    if objects[0].area == objects[1].area:
        # merge it
        frame = SubGrid(GridRegion([GridPoint(objects[0].region.x1, objects[0].region.y1), GridPoint(objects[1].region.x2, objects[1].region.y2)]), grid)
        objects = objects[2:]
    else:
        frame, *objects = objects
    for obj in objects:
        for frame_point in frame.all_points:
            if frame_point.x + obj.width - 1 <= frame.region.x2 and frame_point.y + obj.height - 1 <= frame.region.y2:
                if all(grid[frame_point.y + y - obj.region.y1][frame_point.x + x - obj.region.x1] == grid.background_color for x, y in obj.points):
                    place_object(obj, frame_point.x, frame_point.y, grid)
                    break
    return grid.crop(frame.region)

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py e8686506 fit_it") 
