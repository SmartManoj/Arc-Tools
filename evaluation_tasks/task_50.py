import os
from arc_tools.grid import Grid, detect_objects, Color, move_object, GridRegion, GridPoint
from arc_tools import logger
from arc_tools.plot import plot_grids
def magnetic_current(grid: Grid):
    '''
    Simulates a magnetic current effect on objects in a grid.
    
    Finds a vertical light gray divider line and moves all objects to its left side.
    For objects with inner holes at their right edge, fills the area to the right 
    of the divider with red color, creating a magnetic field visualization.
    
    Args:
        grid: Input grid containing objects and a vertical divider
        
    Returns:
        Modified grid with objects moved and magnetic field effects applied
    '''
    # result = grid.copy()
    objects = detect_objects(grid, ignore_color=Color.GRAY)
    # find gray vertical divider line
    for c in range(grid.width):
        if all(grid[r][c] == Color.GRAY.value for r in range(grid.height)):
            divider_col = c
            break
    # move all objects to the left of the divider line
    for obj in objects:
        obj = move_object(obj, divider_col - obj.width - obj.region.x1, 0, grid)
        holes = detect_objects(Grid(obj))
        # plot_grids([obj, *holes])
        # check if it is inner
        last_inner_hole = None
        for hole in holes:
            if not (hole.region.x1 == 0 or  hole.region.x2 == obj.width - 1 or hole.region.y1 == 0 or hole.region.y2 == obj.height - 1) and hole.region.x2 == obj.width - 2:
                for y in range(hole.region.y1, hole.region.y2+1):
                    for x in range(divider_col + 1, grid.width):
                        grid[y + obj.region.y1][x] = Color.RED.value


    return grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 6e453dd6 magnetic_current") 
