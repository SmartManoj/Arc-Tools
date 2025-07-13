import os
from arc_tools.grid import Color, Grid, GridPoint

# logger.setLevel(10)

def water_flow(grid: Grid):
    """
    pink color is water.
    orange color is slab.
    Water flows downward from initial positions and around red obstacles.
    """
    
    result_grid = grid.copy()
    
    # Find initial water positions
    initial_water = []
    for y in range(grid.height):
        for x in range(grid.width):
            if grid[y][x] == Color.MAGENTA.value and grid[y+1][x] != Color.MAGENTA.value:
                initial_water.append(GridPoint(x, y))
    
    # For each initial water position, create downward flow and channels around obstacles
    for water_pos in initial_water:
        create_water_flow_from_source(result_grid, water_pos)
    
    return result_grid

def create_water_flow_from_source(grid: Grid, source: GridPoint):
    """Create water flow from a source position"""
    
    # Water flows downward from the source until it hits a red obstacle
    # Then it flows around the obstacle creating rectangular channels
    
    # Flow downward from source
    y = source.y
    while y < grid.height:
        if grid[y + 1][source.x] == Color.RED.value:
            # Hit a red obstacle, create channels around it
            create_channels_around_obstacle(grid, source.x, y)
            break
        elif grid[y][source.x] == grid.background_color:
            grid[y][source.x] = Color.MAGENTA.value
        y += 1

def create_channels_around_obstacle(grid: Grid, x: int, y: int):
    """Create channels around a red obstacle"""
    # Create vertical channel
    for dx in range(x, grid.width):
        if grid[y][dx] == Color.RED.value:
            break
        grid[y][dx] = Color.MAGENTA.value
        if grid[y+ 1][dx] != Color.RED.value:
            create_water_flow_from_source(grid, GridPoint(dx, y))
            break
    for dx in range(x-1, -1, -1):
        if grid[y][dx] == Color.RED.value:
            break
        grid[y][dx] = Color.MAGENTA.value
        if grid[y+ 1][dx] != Color.RED.value:
            create_water_flow_from_source(grid, GridPoint(dx, y))
            break



if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 36a08778 water_flow")
    