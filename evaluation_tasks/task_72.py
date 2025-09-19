import os
from arc_tools.grid import Grid, detect_objects
from arc_tools import logger
from arc_tools.plot import plot_grids

def symmetry(grid: Grid):
    '''
    remove dots to create vertical symmetry
    '''
    # Create a copy to work with
    result = grid.copy()

    objects = detect_objects(grid)
    
    for obj in objects:
        # Find the center column
        width = obj.width
        center_col = width // 2
        # For each row, ensure vertical symmetry
        approach_1 = []
        for y in range(obj.height):
            # Check only the left half to avoid double processing
            for x in range(center_col):
                # Calculate the symmetric position on the right side
                symmetric_x = width - 1 - x
                
                # Get colors at both positions
                left_color = obj[y][x]
                right_color = obj[y][symmetric_x]
                
                # If colors don't match and both are non-background, remove both
                if left_color != right_color:
                    if left_color != obj.background_color:
                        approach_1.append((y+obj.region.y1, x+obj.region.x1))
                    if right_color != obj.background_color:
                        approach_1.append((y+obj.region.y1, symmetric_x+obj.region.x1))
        # check left col values, if it is less than approach_1, then remove the left col values
        approach_2 = []
        for y in range(obj.height):
            v = obj[y][0]
            if v != obj.background_color:
                approach_2.append((y+obj.region.y1, 0+obj.region.x1))
        if len(approach_2) <= len(approach_1):
            width2 = width - 1
            center_col2 = width2 // 2
            for y in range(obj.height):
                for x in range(center_col2):
                    symmetric_x = width2 - 1 - x + 1
                    x += 1
                    left_color = obj[y][x]
                    right_color = obj[y][symmetric_x]
                    if left_color != right_color:
                        if left_color != obj.background_color:
                            approach_2.append((y+obj.region.y1, x+obj.region.x1))
                        if right_color != obj.background_color:
                            approach_2.append((y+obj.region.y1, symmetric_x+obj.region.x1))
        
        approach_3 = []
        for y in range(obj.height):
            v = obj[y][obj.width - 1]
            if v != obj.background_color:
                approach_3.append((y+obj.region.y1, width-1+obj.region.x1))
        if len(approach_3) <= len(approach_1):
            width2 = width - 1
            center_col2 = width2 // 2
            for y in range(obj.height):
                for x in range(center_col2):
                    symmetric_x = width2 - 1 - x
                    left_color = obj[y][x]
                    right_color = obj[y][symmetric_x]
                    if left_color != right_color:
                        if left_color != obj.background_color:
                            approach_3.append((y+obj.region.y1, x+obj.region.x1))
                        if right_color != obj.background_color:
                            approach_3.append((y+obj.region.y1, symmetric_x+obj.region.x1))
        if approach_2 and len(approach_2) <= len(approach_1) and len(approach_2) <= len(approach_3):
            approach_1 = approach_2
        elif approach_3 and len(approach_3) <= len(approach_1) and len(approach_3) <= len(approach_2):
            approach_1 = approach_3
        for y, x in approach_1:
            result[y][x] = obj.background_color
        # plot_grids([obj, result])
    return result

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 8e5c0c38 symmetry") 
