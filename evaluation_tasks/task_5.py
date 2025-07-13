from arc_tools.grid import Grid, detect_objects, Color, SubGrid, GridRegion, GridPoint
from arc_tools.logger import logger

def transform_object(obj: SubGrid) -> SubGrid:
    """
    Transform object based on its color and direction
    """
    # Get the object's color
    color = obj.get_max_color()
    
    # Create a new grid for the transformed object
    
    if color == Color.RED.value:
        # (x,x) pattern
        new_grid = [[obj.background_color for _ in range(2)] for _ in range(1)]
        new_grid[0][0] = color
        new_grid[0][1] = color
    elif color == Color.BLUE.value:
        # (x,x,x) pattern
        new_grid = [[obj.background_color for _ in range(3)] for _ in range(1)]
        new_grid[0][0] = color
        new_grid[0][1] = color
        new_grid[0][2] = color
    elif color == Color.MAGENTA.value:
        # vertical pattern
        # x
        # x
        new_grid = [[obj.background_color for _ in range(1)] for _ in range(2)]
        new_grid[0][0] = color
        new_grid[1][0] = color
    elif color == Color.GREEN.value:
        # (x,x,x,x) pattern
        new_grid = [[obj.background_color for _ in range(4)] for _ in range(1)]
        new_grid[0][0] = color
        new_grid[0][1] = color
        new_grid[0][2] = color
        new_grid[0][3] = color
    grid = Grid(new_grid)
    region = GridRegion([
        GridPoint(0, 0),
        GridPoint(grid.width - 1, grid.height - 1)
    ])
    return SubGrid(region, grid)

def mapper(grid: Grid) -> Grid:
    '''
    divide the region using the vertical line
    each object is transformed into another object in right side (randomly?) (just take outputs as it is)
    replace each object in the left side with the transformed object in the right side
    '''
    grid = grid.copy()
    
    # Find the yellow vertical divider line
    divider_x = None
    for x in range(grid.width):
        is_divider = True
        for y in range(grid.height):
            if grid[y][x] != Color.YELLOW.value:
                is_divider = False
                break
        if is_divider:
            divider_x = x
            break
    
    if divider_x is None:
        logger.error("Could not find yellow divider line")
        return grid
    
    
    # Create a region for the left side
    left_region = GridRegion([
        GridPoint(0, 0),
        GridPoint(divider_x - 1, grid.height - 1)
    ])
    
    # Detect objects only in the left region
    left_grid = SubGrid(left_region, grid).get_full_grid()
    left_objects = detect_objects(left_grid)
    
    # Create a region for the right side
    right_region = GridRegion([
        GridPoint(divider_x + 1, 0),
        GridPoint(grid.width - 1, grid.height - 1)
    ])
    
    # Detect objects only in the right region
    right_grid = SubGrid(right_region, grid)
    right_objects = detect_objects(right_grid)
    
    # Sort objects by vertical position
    left_objects.sort(key=lambda obj: obj.region.x1)
    
    # For each left object, replace it with the transformed right object
    new_x, new_y = right_objects[0].region.x1, right_objects[0].region.y1 + 1
    for left_obj in left_objects:
        # Get the color of the right object to determine transformation
        color = left_obj.get_max_color()
        # Transform the right object
        transformed_obj = transform_object(left_obj)
        left_direction = color in [Color.RED.value, Color.GREEN.value]
        if left_direction:
            new_x -= transformed_obj.width - 1
        
        # Remove the left object
        grid.remove_object(left_obj)
        # plot_grids([left_obj, transformed_obj], f"left_obj_{left_obj.get_max_color()}.png",show=True)
        # Place the transformed object at the left object's position
        for y in range(transformed_obj.height):
            for x in range(transformed_obj.width):
                right_grid[new_y + y][new_x + x] = transformed_obj[y][x]
        if not left_direction:
            new_x += transformed_obj.width - 1
        new_y += transformed_obj.height
    return right_grid

if __name__ == "__main__":
    import os
    os.system("main.py 136b0064 mapper")