from arc_tools.grid import Grid, copy_object, detect_objects, SubGrid, GridRegion, GridPoint
# logger.setLevel(logging.DEBUG)
def frame_fit(grid: Grid) -> Grid:
    """ 
    two regions with divider line.
    left side objects.
    right side frame.
    copy the objects by making the center of the object aligns with frame borders and remove it if placed.
    """
    for x in range(grid.width):
        col_colors = list(grid[y][x] for y in range(grid.height) if grid[y][x] != grid.background_color)
        if len(col_colors) == grid.height:
            divider_column = x
            break
    if divider_column is None:
        raise ValueError("No divider column found")
    left_region = SubGrid(GridRegion([GridPoint(0, 0), GridPoint(divider_column-1, grid.height-1)]), grid)
    right_region = SubGrid(GridRegion([GridPoint(divider_column+1, 0), GridPoint(grid.width-1, grid.height-1)]), grid)
    left_objects = detect_objects(left_region, single_color_only=True)
    for obj in left_objects:
        copy_count = 0
        obj_color = obj.get_max_color()
        for y in range(0, right_region.height):
            if right_region[y][0] == obj_color:
                for x in range(0, right_region.width):
                    if right_region[0][x] == obj_color:
                        copy_count += 1
                        # x-radius and y-radius represent the top left corner of the object
                        radius = obj.height//2
                        dx, dy = (right_region.region.x1 + x -radius)-obj.region.x1, (y-radius)-obj.region.y1
                        copy_object(obj, dx, dy, grid, greedy=False)
        if copy_count != 0:
            grid.remove_object(obj)
    return grid

if __name__ == "__main__":
    import os
    os.system("main.py 247ef758 frame_fit")