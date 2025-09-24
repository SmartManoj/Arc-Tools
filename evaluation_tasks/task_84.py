import os
from arc_tools.grid import Color, Grid, detect_objects
from arc_tools.plot import plot_grids

directions = {
    'left': (-1, 0),
    'right': (1, 0),
    'up': (0, -1),
    'down': (0, 1)
}
LIGHT_GRAY = Color.LIGHT_GRAY.value
MAROON = Color.MAROON.value
LIGHT_BLUE = Color.LIGHT_BLUE.value
def find_other_end(point: tuple, direction: str, grid: Grid, obj_color: Color):
    dx, dy = directions[direction]
    x, y = point
    # move until the direction is not grid.background_color
    steps = 0
    pipe_colors = [LIGHT_BLUE, LIGHT_GRAY]
    while steps < 60:
        steps += 1
        if grid[y+dy][x+dx] in [grid.background_color, obj_color]:
            if direction == 'right':
                # check up
                if grid[y-1][x] in pipe_colors:
                    direction = 'up'
                elif grid[y+1][x] in pipe_colors:
                    # check down
                    direction = 'down'
                else:
                    break
                dx, dy = directions[direction]
            elif direction == 'down':
                # check left
                if grid[y][x-1] in pipe_colors:
                    direction = 'left'
                elif grid[y][x+1] in pipe_colors:
                    direction = 'right'
                else:
                    break
                dx, dy = directions[direction]
            elif direction == 'left':
                # check up
                if grid[y-1][x] in pipe_colors:
                    direction = 'up'
                elif grid[y+1][x] in pipe_colors:
                    direction = 'down'
                else:
                    if grid[y][x] != MAROON:
                        break
                    else:
                        # find surrounding values
                        objects = detect_objects(grid, required_color=MAROON)
                        for obj in objects:
                            if obj.contains((x,y)):
                                sp = obj.get_surrounding_points() 
                                # skip horizontal point
                                sp = [p for p in sp if p.y != y][0]
                                if sp.y > y:
                                    direction = 'down'
                                else:
                                    direction = 'up'
                                x , y = sp.x, sp.y
                                # plot_grids([grid, obj])
                                break
                dx, dy = directions[direction]
            elif direction == 'up':
                # check left
                if grid[y][x-1] in pipe_colors:
                    direction = 'left'
                elif grid[y][x+1] in pipe_colors:
                    direction = 'right'
                else:
                    break
                dx, dy = directions[direction]
            
        x += dx
        y += dy

    return x , y

def extractor(grid: Grid):
    '''
    4 dot object and 5 dot object should be joined by light blue pipe.
    '''
    
    objects = detect_objects(grid, ignore_colors=[Color.LIGHT_BLUE, Color.MAROON, Color.LIGHT_GRAY])
    # plot_grids(objects[:])
    for obj in objects:
        td = obj.get_total_dots()
        # if obj.color != 2:
        #     continue
        if td == 9:
            x,y = obj.region.start
            grid[y][x] = grid.background_color
            grid[y][x+2] = grid.background_color
            grid[y+1][x+1] = grid.background_color
            grid[y+2][x] = grid.background_color
            grid[y+2][x+2] = grid.background_color
            td -= 5
        if td == 5:
            # place 4 dot obj on the other end
            x,y = obj.region.start
            if grid[y+1][x-1] == LIGHT_BLUE: # left
                x,y =find_other_end((x-1, y+1), 'left', grid, obj.color)
                grid[y][x-1] = obj.color
                grid[y-1][x-2] = obj.color
                grid[y+1][x-2] = obj.color
                grid[y][x-3] = obj.color
            elif grid[y-1][x+1] == LIGHT_BLUE:
                x,y =find_other_end((x+1, y-1), 'up', grid, obj.color)
                grid[y-1][x] = obj.color
                grid[y-2][x-1] = obj.color
                grid[y-2][x+1] = obj.color
                grid[y-3][x] = obj.color
        elif td == 4:
            # place 5 dot obj on the other end
            x,y = obj.region.end
            if grid[y-1][x+1] == LIGHT_BLUE: # right
                x,y =find_other_end((x+1, y-1), 'right', grid, obj.color)
                # plot_grids([grid,obj])
                grid[y-1][x+1] = obj.color
                grid[y+1][x+1] = obj.color
                grid[y][x+2] = obj.color
                grid[y-1][x+3] = obj.color
                grid[y+1][x+3] = obj.color
            elif grid[y+1][x-1] == LIGHT_BLUE: # bottom
                x,y =find_other_end((x-1, y+1), 'down', grid, obj.color)
                grid[y+1][x-1] = obj.color
                grid[y+1][x+1] = obj.color
                grid[y+2][x] = obj.color
                grid[y+3][x-1] = obj.color
                grid[y+3][x+1] = obj.color
            

    return grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py a47bf94d extractor") 
