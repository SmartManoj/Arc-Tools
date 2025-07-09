import os
from collections import Counter
from arc_tools.grid import Color, Grid, SubGrid, detect_objects, GridRegion, GridPoint, place_object_on_new_grid
from arc_tools import logger
from arc_tools.plot import plot_grids

def seal_the_box(grid: Grid):
    '''
    Detect 5*5 boxes in the grid, find the right color seal (3*3) and seal it in center.
    Returns the boxes region with seals placed.
    '''
    # Detect all objects in the grid
    objects = detect_objects(grid)
    
    boxes = []
    seals = []
    
    for obj in objects:
        if obj.width == 5 and obj.height == 5:
            boxes.append(obj)
        elif obj.width == 3 and obj.height == 3:
            seals.append(obj)

    x1, y1, x2, y2 = boxes[0].region.x1 - 1, boxes[0].region.y1 - 1, boxes[-1].region.x2 + 1, boxes[-1].region.y2 + 1
    
    output_region = GridRegion([GridPoint(x1, y1), GridPoint(x2, y2)])
    output_grid = SubGrid(output_region, grid)

    for box in boxes:
        box_color = box.color
        seal = next(s for s in seals if s.color == box_color)
        place_object_on_new_grid(seal, box.region.x1 - x1 + 1, box.region.y1 - y1 + 1, output_grid, fill_color=grid.background_color)
    
    return output_grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 58f5dbd5 seal_the_box") 
