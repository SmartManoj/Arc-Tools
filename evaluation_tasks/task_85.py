import os
from arc_tools.grid import Grid, GridPoint, GridRegion, detect_objects, Color
from arc_tools import logger
from arc_tools.plot import plot_grids
from collections import defaultdict

def look_through(input_grid: Grid):
    '''
    green frame cover other frames
    return the content inside green frame
    '''
    grid = input_grid.copy()
    green_frame = detect_objects(grid, required_color=Color.GREEN.value, single_color_only=True)[0]
    objects = detect_objects(grid, ignore_colors=[Color.GREEN.value])
    remaining_frames = []
    remaining_frames_color_counter = defaultdict(list)
    for obj in objects:
        remaining_frames.append(obj)
        remaining_frames_color_counter[obj.colors].append(obj)
    
    # Create output region (inside the green frame)
    output_region = GridRegion([GridPoint(green_frame.region.x1+1, green_frame.region.y1+1), GridPoint(green_frame.region.x2-1, green_frame.region.y2-1)])
    for frame in remaining_frames:
        if not frame.get_background_dots_count():
            continue
        if len(remaining_frames_color_counter[frame.colors]) > 1:
            obj1, obj2 = remaining_frames_color_counter[frame.colors]
            # if x1 is same, then add vertical lines
            if obj1.region.x1 == obj2.region.x1:
                for y in range(obj1.region.y2, obj2.region.y1):
                    grid[y][obj1.region.x1] = frame.color
                    grid[y][obj1.region.x2] = frame.color
            elif obj1.region.y1 == obj2.region.y1:
                for x in range(obj1.region.x2, obj1.region.x1):
                    grid[obj1.region.y1][x] = frame.color
                    grid[obj1.region.y2][x] = frame.color
        else:
            colors = frame.colors
            for points in frame.get_border_points():
                grid[points.y][points.x] = colors[(points.x+points.y)% len(colors)]
            # plot_grids([grid, frame])
            
    
    
    output_grid = grid.crop(output_region)
    return output_grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py a6f40cea look_through") 
