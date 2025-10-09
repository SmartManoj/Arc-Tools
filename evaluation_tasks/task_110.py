from mimetypes import init
import os
from arc_tools.grid import Grid, detect_objects, Color
from arc_tools import logger
from arc_tools.plot import plot_grids

def colliding_rays(grid: Grid):
    '''
    Extend rays from ray boxes.
    When two diagonal rays collide, they continue straight (vertical/horizontal).
    '''
    result = grid.copy()
    
    objects = detect_objects(grid)
    dir_map = {
            (0,0): (-1, -1),
            (1,0): (0, -1),
            (2,0): (0, -1),
            (3,0): (1, -1),
            (0,1): (-1, 0),
            (3,1): (1, 0),
            (0,2): (-1, 0),
            (3,2): (1, 0),
            (0,3): (-1, 1),
            (1,3): (0, 1),
            (2,3): (0, 1),
            (3,3): (1, 1),
        }
    ray_map = {}
    seconday_values = {}
    def extend_ray(ray_color, x, y, dx, dy, bend=0, from_divert=1, hbend=0):
        count = 0
        while 0 <= x < grid.width and 0 <= y < grid.height:
            if result[y][x] == grid.background_color or (from_divert and grid[y][x] == grid.background_color):
                ray_map[(x, y)] = (dx, dy)
                result[y][x] = ray_color
            elif result[y][x] != grid.background_color:
                seconday_values[(x, y)] = ray_color
            x += dx
            count += 1
            if bend == 1 and count % 2 == 0:
                x-=1
            if hbend == 1 and count % 2 == 0:
                y-=1
            y += dy
    box_border_color = objects[0].get_border_points()[0].value
    for obj in objects:
        ray_color = obj[1][1]
        for y in range(obj.width):
            for x in range(obj.width):
                if obj[y][x] != box_border_color and (x, y) in dir_map:
                    dx, dy = dir_map[(x, y)]
                    extend_ray(ray_color, obj.region.x1 + x, obj.region.y1 + y, dx, dy, from_divert=0)
    def divert_ray(ray_color, x, y, dx, dy):
        collision_detected = 0
        while 0 <= x < grid.width and 0 <= y < grid.height:
            
            if collision_detected == 1:
                if result[y][x] == ray_color:
                    secondary_value = seconday_values.get((x, y))
                    if [p.value for p in result.get_surrounding_points(y, x)].count(secondary_value) <=0 or secondary_value == ray_color:
                        secondary_value = grid.background_color
                    result[y][x] = secondary_value
            if collision_detected == 0:
                if (dx, dy) == (1, -1):
                    if result[y][x+1] not in [grid.background_color, []] and ray_map.get((x+1, y)) == (0, -1):
                        extend_ray(ray_color, x-1, y+1, 1, -1, bend=1)
                        collision_detected = 1
                    elif result[y][x+1] not in [grid.background_color, []] and ray_map.get((x+1, y)) == (- 1, -1):
                        extend_ray(ray_color, x, y, 0, -1)
                        collision_detected = 1
                if (dx, dy) == (-1, -1):
                    if result[y][x-1] not in [grid.background_color, []]:
                        extend_ray(ray_color, x, y-1, 0, -1)
                        collision_detected = 1
                if (dx, dy) == (1, 1):
                    if result[y][x+1] not in [grid.background_color, []] and ray_map.get((x+1, y)) == (0, 1):
                        extend_ray(ray_color, x-1, y-1, 1, 1, bend=1)
                        collision_detected = 1
                    elif result[y+1][x] not in [grid.background_color, []] and ray_map.get((x, y+1)) == (1, 0):
                        extend_ray(ray_color, x-1, y-1, 1, 1, hbend=1)
                        collision_detected = 1
                    elif result[y][x+1] not in [grid.background_color, []] and ray_map.get((x+1, y)) == (-1, 1):
                        extend_ray(ray_color, x, y, 0, 1)
                        collision_detected = 1
                if (dx, dy) == (-1, 1):
                    if result[y][x-1] not in [grid.background_color, []]:
                        extend_ray(ray_color, x, y, 0, 1)
                        collision_detected = 1
                if (dx, dy) == (1, 0):
                    if result[y+1][x+1] not in [grid.background_color, []] and ray_map.get((x+1, y+1)) == (0, 1):
                        old_ray_color = ray_color
                        ray_color = result[y-1][x+1]
                        for y1 in range(y, grid.height):
                            result[y1][x+1] = grid.background_color
                        extend_ray(ray_color, x+1, y-1, 1, 1)
                        ray_color = result[y-1][x+2]
                        for y1 in range(y, grid.height):
                            if result[y1][x+2] == ray_color:
                                result[y1][x+2] = grid.background_color
                        extend_ray(ray_color, x+2, y-1, 1, 1)
                        ray_color = old_ray_color
                        extend_ray(ray_color, x, y, 1, 1)
                        collision_detected = 1
                    elif result[y+1][x+1] not in [grid.background_color, []] and ray_map.get((x+1, y+1)) == (0, -1):
                        extend_ray(ray_color, x + 1, y - 1, 1, -1)
                        collision_detected = 1
                    elif result[y-1][x-1] not in [grid.background_color, []] and ray_map.get((x, y-1)) == (1, 1):
                        extend_ray(ray_color, x+1, y, 1, 1, hbend=1)
                        collision_detected = 1
                        
                if (dx, dy) == (0, -1):
                    if result[y+1][x-1] not in [grid.background_color, []] and result[y+1][x-1] != grid[y+1][x-1] and ray_map.get((x-1, y+1)) == (1, -1):
                        extend_ray(ray_color, x, y, 1, -1, bend=1)
                        collision_detected = 1
                    elif result[y-1][x-1] not in [grid.background_color, []] and result[y-1][x-1] != grid[y-1][x-1] and ray_map.get((x-1, y-1)) == (1, 0):
                        extend_ray(ray_color, x, y, 1, -1)
                        collision_detected = 1
                    elif result[y-1][x+1] not in [grid.background_color, []] and result[y-1][x+1] != grid[y-1][x+1] and ray_map.get((x-1, y-1)) == (-1, 0):
                        extend_ray(ray_color, x, y, -1, -1)
                        collision_detected = 1
                if (dx, dy) == (0, 1):
                    if result[y-1][x-1] not in [grid.background_color, []] and result[y-1][x-1] != grid[y-1][x-1] and ray_map.get((x-1, y-1)) == (1, 1):
                        extend_ray(ray_color, x, y, 1, 1, bend=1)
                        collision_detected = 1
                    elif result[y+1][x-1] not in [grid.background_color, []] and result[y+1][x-1] != grid[y-1][x-1] and ray_map.get((x+1, y+1)) == (1, 0):
                        extend_ray(ray_color, x, y, 1, 1)
                        collision_detected = 1
                if (dx, dy) == (-1, 0):
                    if result[y+1][x-1] not in [grid.background_color, []] and result[y+1][x-1] != grid[y+1][x-1]:
                        extend_ray(ray_color, x, y, -1, -1)
                        collision_detected = 1
            x += dx
            y += dy
    # plot_grids([grid, result])
    for obj in objects:
        ray_color = obj[1][1]
        for y in range(obj.width):
            for x in range(obj.width):
                if obj[y][x] != box_border_color and (x, y) in dir_map:
                    dx, dy = dir_map[(x, y)]
                    divert_ray(ray_color, obj.region.x1 + x, obj.region.y1 + y, dx, dy)

    return result

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py e12f9a14 colliding_rays") 
