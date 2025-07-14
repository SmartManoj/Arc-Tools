import os
from arc_tools import logger
from arc_tools.grid import BorderSide, Grid, GridPoint, GridRegion, SubGrid, copy_object, detect_objects, Color, move_object
from arc_tools.plot import plot_grids

def land_the_ship(grid: Grid):
    '''
    maroon object is the docker.
    lightblue object is the ship.
    '''
    # Create a copy to work with
    ship_color = Color.LIGHTBLUE.value
    objects = detect_objects(grid)
    dockers = []
    walls = []
    ships = []
    for obj in objects:
        if obj.color == Color.MAROON.value:
            dockers.append(obj)
        elif obj.width >= grid.width - 4 or obj.height >= grid.height - 4:
            # ignore middle walls 
            if obj.region.x1 == 0 or obj.region.x2 == grid.width - 1 or obj.region.y1 == 0 or obj.region.y2 == grid.height - 1:
                walls.append(obj)
    # subgrid 2*2
    has_top_wall = grid[0][2] != grid.background_color
    has_left_wall = grid[2][0] != grid.background_color
    has_bottom_wall = grid[grid.height - 1][2] != grid.background_color
    has_right_wall = grid[2][grid.width - 1] != grid.background_color
    x1 = 2 if has_left_wall else 0   
    x2 = grid.width - 3 if has_right_wall else grid.width - 1
    y1 = 2 if has_top_wall else 0
    y2 = grid.height - 3 if has_bottom_wall else grid.height - 1
    subgrid = SubGrid(GridRegion([GridPoint(x1,y1),GridPoint(x2,y2)]), grid)
    ships = detect_objects(subgrid) 
    ships = [ship for ship in ships if ship.width < grid.width - 4 and ship.height < grid.height - 4 and ship.color != Color.MAROON.value]
    for ship in ships:
        grid.remove_object(ship)
    clean_grid = grid.copy()
    for ship in ships:
        for docker in dockers:
            docker_count = docker.get_values_count()[Color.MAROON.value]
            if ship.get_values_count()[Color.MAROON.value] == docker_count:
                # rotate the ship based on the wall
                # find from docker itself.
                x = docker.region.x1
                first_wall_color = None
                for y in reversed(range(docker.region.y1)):
                    if clean_grid[y][x] not in [Color.MAROON.value, grid.background_color]:
                        first_wall_color = clean_grid[y][x]
                        first_wall_side = 'top' 
                        break
                if first_wall_color is None:
                    y = docker.region.y1
                    for x in reversed(range(docker.region.x1)):
                        if clean_grid[y][x] not in [Color.MAROON.value, grid.background_color]:
                            first_wall_color = clean_grid[y][x]
                            first_wall_side = 'left'
                            break
                last_wall_color = None
                x = docker.region.x2
                for y in range(docker.region.y2, grid.height):
                    if clean_grid[y][x] not in [Color.MAROON.value, grid.background_color]:
                        last_wall_color = clean_grid[y][x]
                        last_wall_side = 'bottom'
                        break
                if last_wall_color is None:
                    y = docker.region.y2
                    for x in range(docker.region.x2, grid.width):
                        if clean_grid[y][x] not in [Color.MAROON.value, grid.background_color]:
                            last_wall_color = clean_grid[y][x]
                            last_wall_side = 'right'
                            break
                for _ in range(4):
                    side_data_1 = list(set(i for i in ship.get_side_data(BorderSide(first_wall_side)) if i not in [grid.background_color, Color.MAROON.value]))
                    if len(side_data_1) == 1:
                        side_color_1 = side_data_1[0]
                    else:
                        side_color_1 = None
                    side_data_2 = list(set(i for i in ship.get_side_data(BorderSide(last_wall_side)) if i not in [grid.background_color, Color.MAROON.value]))
                    if len(side_data_2) == 1:
                        side_color_2 = side_data_2[0]
                    else:
                        side_color_2 = None
                    if side_color_1 == first_wall_color or side_color_2 == last_wall_color:
                        if first_wall_side == 'top':
                            # check left and right side 
                            left_side_data = list(set(i for i in ship.get_side_data(BorderSide.LEFT) if i not in [grid.background_color, Color.MAROON.value]))
                            flipped = False
                            left_wall_color = None
                            if len(left_side_data) == 1:
                                left_side_color = left_side_data[0]
                                for x in reversed(range(docker.region.x1)):
                                    if clean_grid[y1][x] not in [Color.MAROON.value, grid.background_color]:
                                        left_wall_color = clean_grid[y1][x]
                                        break
                                if left_side_color != left_wall_color and left_side_color != ship_color:
                                    ship = ship.flip_vertically()
                                    flipped = True
                            if not flipped:
                                right_side_data = list(set(i for i in ship.get_side_data(BorderSide.RIGHT) if i not in [grid.background_color, Color.MAROON.value]))
                                right_wall_color = None
                                if len(right_side_data) == 1:
                                    right_side_color = right_side_data[0]
                                    for x in range(docker.region.x2, grid.width):
                                        if clean_grid[y1][x] not in [Color.MAROON.value, grid.background_color]:
                                            right_wall_color = clean_grid[y1][x]
                                            break
                                    if right_side_color != right_wall_color and right_side_color != ship_color:
                                        ship = ship.flip_vertically()
                                        flipped = True
                            if not flipped:
                                # check top and bottom side
                                top_side_data = list(set(i for i in ship.get_side_data(BorderSide.TOP) if i not in [grid.background_color, Color.MAROON.value]))
                                top_wall_color = None
                                if len(top_side_data) == 1:
                                    top_side_color = top_side_data[0]
                                    for y in reversed(range(docker.region.y1)):
                                        if clean_grid[y][x1] not in [Color.MAROON.value, grid.background_color]:
                                            top_wall_color = clean_grid[y][x1]
                                            break
                                    if top_side_color != top_wall_color and top_side_color != ship_color:
                                        ship = ship.flip_horizontally()
                                        flipped = True
                            if not flipped:
                                # check bottom and top side
                                bottom_side_data = list(set(i for i in ship.get_side_data(BorderSide.BOTTOM) if i not in [grid.background_color, Color.MAROON.value]))
                                bottom_wall_color = None
                                if len(bottom_side_data) == 1:
                                    bottom_side_color = bottom_side_data[0]
                                    for y in range(docker.region.y2, grid.height):
                                        if clean_grid[y][x1] not in [Color.MAROON.value, grid.background_color]:
                                            bottom_wall_color = clean_grid[y][x1]
                                            break
                                    if bottom_side_color != bottom_wall_color and bottom_side_color != ship_color:
                                        ship = ship.flip_horizontally()
                                        flipped = True


                        
                        break

                    ship = ship.anti_rotate()

                # get marron pos
                for x in range(ship.width):
                    if (y := next((y for y in range(ship.height) if ship[y][x] == Color.MAROON.value),None)) is not None:
                        copy_object(ship, docker.region.x1 - ship.region.x1 - x, docker.region.y1 - ship.region.y1 - y , grid)
                        break


    return grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 6e4f6532 land_the_ship") 
