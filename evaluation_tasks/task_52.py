from collections import Counter, defaultdict
import os
from arc_tools.grid import Grid, GridRegion, GridPoint, SubGrid, detect_objects, place_object_on_new_grid
from arc_tools import logger
from arc_tools.plot import plot_grids
# logger.setLevel(10)
def extract_frames(grid: Grid):
    # check every layer from outside to inside
    frame_length = []
    frame_colors = []
    last_color = None
    for i in range(grid.height//2):
        # horizontal_data
        data = [grid[i][j] for j in range(i, grid.height - i) if grid[i][j] != grid.background_color]
        if not data:
            # vertical data
            data = [grid[j][i] for j in range(i, grid.width - i) if grid[j][i] != grid.background_color]

        data_color = next(iter(data), None)
        data_check = [data_item != last_color for data_item in data]
        if any(data_check):
            last_color = data_color
            frame_length.append(1)
            frame_colors.append(last_color)
        else:
            frame_length[-1] += 1
    frames = []
    for i, color in enumerate(frame_colors):
        lfs = sum(frame_length[:i]) # last_frame_size
        region = GridRegion([GridPoint(lfs, lfs), GridPoint(grid.width - lfs - 1, grid.height - lfs - 1)])
        frames.append(SubGrid(region, grid, color))
    return frames


def smart_rotate(grid: Grid):
    '''
    add the function description first.
    '''
    objects = detect_objects(grid, single_color_only=1)
    
    # sort by area
    n_frames = len(objects) // 2
    object_distribution_by_color = defaultdict(list)
    for obj in objects:
        object_distribution_by_color[obj.color].append(obj)
    
    # it is away from main object.
    objects1 = detect_objects(grid, single_color_only=0)
    objects1.sort(key=lambda x: x.area, reverse=True)
    main_ojbect = objects1[0]
    
    rotation_map_objects = []
    for color in object_distribution_by_color:
        if len(object_distribution_by_color[color]) >= 2:
            object_group = object_distribution_by_color[color]
            object_group.sort(key=lambda x: abs(x.region.x1 - main_ojbect.region.x1) + abs(x.region.y1 - main_ojbect.region.y1), reverse=True)
            if not main_ojbect.contains(object_group[0]):
                rotation_map_objects.append(object_group[0])
    # remove it
    for obj in rotation_map_objects:
        grid.remove_object(obj)
    grid = grid.shrink()
    objects = extract_frames(grid)
    rotation_map = {obj.color: obj.get_total_dots() for obj in  rotation_map_objects}
    for obj in objects:
        if obj.color not in rotation_map:
            continue
        obj = obj.expand()
        grid.remove_object(obj)
        x1, y1 = obj.region.x1, obj.region.y1
        for _ in range(rotation_map[obj.color]):
            obj = obj.rotate()
        place_object_on_new_grid(obj, x1, y1, grid)
        # plot_grids([grid, obj])
        
    return grid.shrink()

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 6ffbe589 smart_rotate") 
