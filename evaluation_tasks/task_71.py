from dis import HAVE_ARGUMENT
import os
from arc_tools import plot
from arc_tools.grid import Grid, detect_objects
from arc_tools.plot import plot_grids

def projector(grid: Grid):
    '''
    Project from projectors (smallest objects) to nearest screen centers and remove unused projectors.
    '''
    objects = detect_objects(grid)
    projector_color = min(objects, key=lambda x: x.area).color
    projectors = []
    screens = []
    for obj in objects:
        if obj.color == projector_color:
            projectors.append(obj)
        else:
            screens.append(obj)
    
    # Find screen projection points
    projector_points = []
    for screen in screens:
        # Project to the screen center
        if screen.width > screen.height:
            orientation = 'top' if screen[0][0] != grid.background_color else 'bottom'
            if orientation == 'top':
                # choose second layer; 
                row = 1
                for col in range(screen.region.x1 + 2, screen.region.x2 - 1):
                    if grid[row + screen.region.y1][col] != grid.background_color:
                        # project to bottom if there is a projector
                        projector_point = None
                        depth = 0
                        for y in range(row + screen.region.y1, grid.height):
                            if (grid[y][col] == projector_color ):
                                projector_point = (col, y)
                                depth += 1
                            else:
                                if depth:
                                    break
                        if projector_point:
                            projector_points.append(projector_point)
                            for d in range(depth):
                                grid[row+screen.region.y1 + d + 1][col] = projector_color
                            for y in range(row + screen.region.y1 + depth + 1, projector_point[1]+1):
                                grid[y][col] = 0
            else:
                row = screen.height - 2
                for col in range(screen.region.x1 + 2, screen.region.x2 - 1):
                    if grid[row+screen.region.y1][col] != grid.background_color:
                        projector_point = None
                        depth = 0
                        for y in reversed(range(0, row + screen.region.y1 + 1)):
                            if (grid[y][col] == projector_color ):
                                projector_point = (col, y)
                                depth += 1
                            else:
                                if depth:break
                        if projector_point:
                            projector_points.append(projector_point)
                            for d in range(depth):
                                grid[row+screen.region.y1 - d - 1][col] = projector_color
                            for y in reversed(range(projector_point[1], row + screen.region.y1 - depth)):
                                grid[y][col] = 0
        else:
            orientation = 'left' if screen[0][0] != grid.background_color else 'right'
            if orientation == 'left':
                col = 1
                for row in range(screen.region.y1 + 2, screen.region.y2 - 1):
                    if screen[row - screen.region.y1][col] != grid.background_color:
                        projector_point = None
                        depth = 0
                        for x in range(col + screen.region.x1, grid.width):
                            if (grid[row][x] == projector_color ):
                                projector_point = (x, row)
                                depth += 1
                            else:
                                if depth:break
                        if projector_point:
                            projector_points.append(projector_point)
                            for d in range(depth):
                                grid[row][col+screen.region.x1 + d + 1] = projector_color
                            for x in reversed(range(col + screen.region.x1 + d + 2, projector_point[0]+1)):
                                grid[row][x] = 0
            else:
                col = screen.width - 2
                for row in range(screen.region.y1 + 2, screen.region.y2 - 2):
                    if grid[row][col + screen.region.x1] != grid.background_color:
                        projector_point = None
                        depth = 0
                        for x in reversed(range(0,col + screen.region.x1 + 1)):
                            if (grid[row][x] == projector_color ):
                                projector_point = (x, row)
                                depth += 1
                            else:
                                if depth:break
                        if projector_point:
                            projector_points.append(projector_point)
                            for d in range(depth):
                                grid[row][col+screen.region.x1 - d - 1] = projector_color
                            for y in reversed(range(projector_point[0], col + screen.region.x1 - depth)):
                                grid[row][y] = 0
                            grid[row][y-1] = grid.background_color
    # logger.info(f"Projector points: {projector_points}")
    for projector in projectors:
        is_used = any(projector.contains(point) for point in projector_points)
        # logger.info(f"Projector {projector.region} is used: {is_used}")                           
        if not is_used:
            grid.remove_object(projector)
    # plot_grids([grid])
    return grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 8b9c3697 projector") 
