import os
from arc_tools.grid import Grid, detect_objects, Color
from arc_tools.plot import plot_grids

def safe_distance(grid: Grid):
    '''
    green dot is extended to the other edge. in between in BR lines, no of blue dots in that line means the region is resticted to that length.
    '''
    objects = detect_objects(grid)
    # sort by area
    objects.sort(key=lambda x: x.area)
    green_dot, br_lines = objects[0], objects[1:]
    restricted_regions = []
    for br_line in br_lines:
        blue_count = br_line.get_values_count()[Color.BLUE.value]
        # expand blue_count around all regions
        restricted_region = br_line.region.expand(blue_count)
        restricted_regions.append(restricted_region)
        br_line.replace_color(Color.BLUE.value, Color.RED.value)
    # move from green dot to the other edge
    if green_dot.region.y1 == 0:
        # top region
        # move down
        x = green_dot.region.x1
        for y in range(green_dot.region.y1, grid.height):
                grid[y][x] = Color.GREEN.value
                # check all restricted regions
                for restricted_region in restricted_regions:
                    if restricted_region.contains((x, y+1)):
                        # go to first point
                        if not restricted_region.x1 <= 0:
                            for x in range(x, restricted_region.x1 - 2, -1):
                                grid[y][x] = Color.GREEN.value
                        else:
                            for x in range(x, restricted_region.x2 + 2):
                                grid[y][x] = Color.GREEN.value
                        break
    elif green_dot.region.x1 == 0:
        # left region
        # move right
        y = green_dot.region.y1
        for x in range(green_dot.region.x1, grid.width):
            grid[y][x] = Color.GREEN.value
            # check all restricted regions
            for restricted_region in restricted_regions:
                if restricted_region.contains((x+1, y)):
                    if not restricted_region.y1 <= 0:
                        # go to first point
                        for y in range(y, restricted_region.y1 - 2, -1):
                            grid[y][x] = Color.GREEN.value
                    else:
                        # go down
                        for y in range(y, restricted_region.y2 + 2):
                            grid[y][x] = Color.GREEN.value
                    break
    elif green_dot.region.x2 == grid.width - 1:
        # right region
        # move left
        y = green_dot.region.y1
        for x in range(green_dot.region.x2, -1, -1):
            grid[y][x] = Color.GREEN.value
            # check all restricted regions
            for restricted_region in restricted_regions:
                if restricted_region.contains((x-1, y)):
                    if not restricted_region.y1 <= 0:
                        # go to first point
                        for y in range(y, restricted_region.y1 - 2, -1):
                            grid[y][x] = Color.GREEN.value
                    else:
                        # go down
                        for y in range(y, restricted_region.y2 + 2):
                            grid[y][x] = Color.GREEN.value
                    break
    else:
        # bottom region
        # move up
        x = green_dot.region.x1
        for y in range(green_dot.region.y2, -1, -1):
            grid[y][x] = Color.GREEN.value
            # check all restricted regions
            for restricted_region in restricted_regions:
                if restricted_region.contains((x, y-1)):
                    if not restricted_region.y1 <= 0:
                        # go to first point
                        for y in range(y, restricted_region.y1 - 2, -1):
                            grid[y][x] = Color.GREEN.value
                    else:
                        # go down
                        for y in range(y, restricted_region.y2 + 2):
                            grid[y][x] = Color.GREEN.value
                    break
    return grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py cb2d8a2c safe_distance") 
