import os
from arc_tools.grid import Grid, detect_objects, place_object_on_new_grid
from arc_tools import logger
from arc_tools.plot import plot_grids

def move_the_frames(grid: Grid):
    '''
    Move frames from input to correct regions in a chart layout.
    '''
    # Detect all objects in the input grid
    objects = detect_objects(grid)
    
    if len(objects) < 2:
        return grid
    
    # Sort objects by area (largest first)
    objects = sorted(objects, key=lambda obj: obj.area, reverse=True)
    
    # The largest object should be the chart background with 6 regions
    chart = Grid(objects[0])
    chart.background_color = grid.background_color
    frames = objects[1:]
    
    # Get chart regions (should be 6 rectangular regions in 2x3 layout)
    regions = detect_objects(chart, single_color_only=True)
    
    # Count holes in each region (background color cells within the region)
    regions_hole_counts = []
    for region in regions:
        hole_count = region.get_values_count(1)[grid.background_color]
        regions_hole_counts.append(hole_count)
    
    
    # Count holes in each frame
    frame_hole_counts = []
    for i, frame in enumerate(frames):
        hole_count = frame.get_holes_count()
        frame_hole_counts.append(hole_count)
    # Create a copy of the chart to work with
    result = chart.copy()
    
    # Match frames to regions based on hole counts
    used_regions = set()
    
    for i, (frame, frame_holes) in enumerate(zip(frames, frame_hole_counts)):
        # Find matching region
        best_region_idx = None
        for j, region_holes in enumerate(regions_hole_counts):
            if region_holes == frame_holes and j not in used_regions:
                best_region_idx = j
                break
        
        
        if best_region_idx is not None:
            used_regions.add(best_region_idx)
            target_region = regions[best_region_idx]
            
            
            # Calculate center of the target region
            region_center_x = target_region.region.x1 + target_region.width // 2
            region_center_y = target_region.region.y1 + target_region.height // 2
            
            # Calculate offset to center the frame
            offset_x = region_center_x - frame.width // 2
            offset_y = region_center_y - frame.height // 2
            
            
            # Place the frame centered in the region
            frame = frame.replace_color(grid.background_color, target_region.color, replace_in_parent_grid=0)
            # log target region color
            # plot_grids([frame, target_region])
            place_object_on_new_grid(frame, offset_x, offset_y, result)
            # plot_grids([result, frame, grid, target_region])
    
    # Return the result
    return result


if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 8698868d move_the_frames") 
