import os
from arc_tools.grid import Grid, detect_objects, place_object
from arc_tools import logger
from arc_tools.plot import plot_grids

def replicate(input_grid: Grid):
    '''
    Remove horizontal and vertical strips from the grid.
    Identify the matching shapes from shapes frame and place them on the dots frame.
    Return the dots frame.
    '''
    grid = input_grid.copy()
    # remove strips
    first_row = grid[0]
    if len(set(first_row)) == 1:
        # horizontal strip
        for row in range(grid.height):
            first_color = grid[row][0]
            for col in range(grid.width):
                if grid[row][col] == first_color and not(grid[row -1][col] == first_color or grid[row +1][col] == first_color):
                        grid[row][col] = 0
    else:
        # vertical strip
        for col in range(grid.width):
            first_color = grid[0][col]
            border_start = None
            for row in range(grid.height):
                v = grid[row][col]
                if v == first_color and not(grid[row][col -1] == first_color or grid[row][col +1] == first_color) and not border_start:
                        grid[row][col] = 0
                elif not border_start:
                    border_start = v
                elif (grid[row][col -1] == v or grid[row][col +1] == v) and v== border_start:
                    border_start = None
                
    grid.background_color = 0
    frames = detect_objects(grid)
    # plot_grids([grid,*frames])
    shapes = []
    for frame in frames:
        frame1 = Grid(frame)
        inner_color = frame[1][1]
        objects = detect_objects(frame1, ignore_color=inner_color)[1:]
        # plot_grids([frame,*objects])
        if objects[0].area == 1:
            dots = objects
            dots_frame = frame
            # plot_grids([dots_frame])
        else:
            shapes.extend(objects)
    
    
    # find dot position in shape
    for dot in dots:
        def match_shape_position(shape, dot):
            for row in range(shape.height):
                for col in range(shape.width):
                    if shape[row][col] == dot.color:
                        return row, col
            return None, None
        for shape in shapes:
            row, col = match_shape_position(shape, dot)
            if row:
                break
            
        shape = shape.replace_color(shape.background_color, dot.background_color, replace_in_parent_grid=False)
        # plot_grids([shape])
        place_object(shape, dot.region.x1 - col + dots_frame.region.x1, dot.region.y1 - row + dots_frame.region.y1, grid)
    # add dot to grid
    output = grid.crop(dots_frame.region)   
    # plot_grids([grid,*objects])
    return output

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py a251c730 replicate") 
