import os
from collections import defaultdict
from arc_tools import plot
from arc_tools.grid import Grid, SubGrid, detect_objects, move_object, Color
from arc_tools import logger
from arc_tools.grid import GridRegion, GridPoint
from arc_tools.plot import plot_grids

def split_into_lines(obj: SubGrid) -> list[SubGrid]:
    """
    Split an L-shaped object into horizontal and vertical lines.
    The horizontal line is at (0,0) and extends rightward.
    The vertical line extends downward from the end of the horizontal line.
    """
    result = []
    # 4 types of L
    if obj[0][0] == obj.background_color: 
        # vertical line is last col except the last row
        # horizontal line is bottom row
        vertical_region = GridRegion([(obj.region.x2, obj.region.y1), (obj.region.x2, obj.region.y2 - 1)])
        horizontal_region = GridRegion([(obj.region.x1, obj.region.y2), (obj.region.x2, obj.region.y2 )])
    elif obj[obj.height-1][0] == obj.background_color:
        # horizontal line is top row except the first col
        # vertical line is last col
        vertical_region = GridRegion([(obj.region.x2, obj.region.y1), (obj.region.x2, obj.region.y2 )])
        horizontal_region = GridRegion([(obj.region.x1, obj.region.y1), (obj.region.x2 - 1, obj.region.y1 )])
    elif obj[0][obj.width-1] == obj.background_color:
        # vertical line is first col except the last row
        # horizontal line is bottom row
        vertical_region = GridRegion([(obj.region.x1, obj.region.y1), (obj.region.x1, obj.region.y2 - 1)])
        horizontal_region = GridRegion([(obj.region.x1, obj.region.y2), (obj.region.x2, obj.region.y2 )])
    else:
        # horizontal line is top row except the first col
        # vertical line is first col 
        vertical_region = GridRegion([(obj.region.x1, obj.region.y1), (obj.region.x1, obj.region.y2 )])
        horizontal_region = GridRegion([(obj.region.x1 + 1, obj.region.y1), (obj.region.x2, obj.region.y1 )])
    result.append(SubGrid(vertical_region, obj.parent_grid, obj.color))
    result.append(SubGrid(horizontal_region, obj.parent_grid,obj.color))

    return result

def remove_the_stick(grid: Grid):
    '''
    remove color is the color of the first cell in the grid
    remove the sticks with remove color and make sure the remaining objects are fall down
    '''
    # Find all objects
    input_grid = grid.copy()
    remove_hint = detect_objects(grid)[0]
    remove_colors = remove_hint.colors
    for _ in range(4):
        objects = detect_objects(grid, single_color_only=1, go_diagonal=0)[len(remove_colors):]
        horizontal_lines = []
        vertical_lines = []
        lines = []
        for obj in objects:
            logger.debug(f'Processing object: {obj}')
            if not (obj.width > 1 and obj.height > 1):
                if obj.width == 1:
                    vertical_lines.append(obj)
                else:
                    horizontal_lines.append(obj)
                lines.append(obj)
                continue
            _lines = split_into_lines(obj)
            logger.debug(f'Split into lines: {[str(line) for line in _lines]}')
            vertical_lines.append(_lines[0])
            horizontal_lines.append(_lines[1])
            lines.extend(_lines)
        
    
        
        horizontal_attachement_lines = defaultdict(list)
        h_line_heights = {}
        for v_line in vertical_lines:
            for h_line in horizontal_lines:
                if (v_line.region.x1 == h_line.region.x1 - 1 or v_line.region.x1 == h_line.region.x2 + 1) and v_line.region.y1 == h_line.region.y1:
                    if h_line.color in remove_colors:
                        h_line_heights[h_line] = v_line.height
                        continue
                    horizontal_attachement_lines[v_line].append(h_line)
        vertical_attachement_lines = defaultdict(list)
        vertical_attachement_h_lines = defaultdict(list)
        for h_line in horizontal_lines:
            for v_line in vertical_lines:
                if v_line.color in remove_colors:
                    continue
                if h_line.region.y1 == v_line.region.y2 + 1 and h_line.region.x1 <= v_line.region.x1 <= h_line.region.x2:
                    vertical_attachement_lines[h_line].append(v_line)
            for h_line2 in horizontal_lines:
                if h_line2.color in remove_colors:
                    continue
                if h_line.color == Color.RED.value and h_line2.color == Color.LIGHT_GRAY.value:
                    logger.debug(f'h_line: {h_line}')
                    logger.debug(f'h_line2: {h_line2}')
                    logger.debug(f'{h_line.region.y1 == h_line2.region.y2 + 1 and h_line.region.x1 <= h_line2.region.x1 <= h_line.region.x2}')
                if h_line.region.y1 == h_line2.region.y2 + 1 and h_line.region.x1 <= h_line2.region.x1 <= h_line.region.x2:
                    vertical_attachement_h_lines[h_line].append(h_line2)
            
        vertical_top_attachment_lines = defaultdict(list)
        for v_line1 in vertical_lines:
            for v_line2 in vertical_lines:
                if v_line2.color in remove_colors:
                    continue
                if v_line1.region.y1 == v_line2.region.y2 + 1 and v_line1.region.x1 == v_line2.region.x1:
                    vertical_top_attachment_lines[v_line1].append(v_line2)
        # exit()
        for line in lines:
            move_counts = defaultdict(list)
            if line.color in remove_colors:
                # Track move counts for each object
                logger.debug(f'test {line}')
                dy = line.region.height - 1
                if not dy:
                    if line not in h_line_heights:
                        plot_grids([grid, line])
                    dy = h_line_heights[line]
                    
                grid.remove_object(line)
                queue = [(line, dy)]
                while queue:
                    line, length = queue.pop(0)
                    logger.debug(f'vline: {line}')
                    if line.height != 1:
                        h_lines = horizontal_attachement_lines.get(line)
                        if h_lines:
                            queue.extend([(h_line, length) for h_line in h_lines])
                            for h_line in h_lines:
                                # Add move count for this object
                                move_counts[h_line].append(length)
                        v_lines = vertical_top_attachment_lines.get(line)
                        if v_lines:
                            if len(remove_colors) != 2: # TODO: why? 
                                length = length + 1
                            queue.extend([(v_line, length) for v_line in v_lines])
                            for v_line in v_lines:
                                # Add move count for this object
                                move_counts[v_line].append(length)
                    else:
                        v_lines = vertical_attachement_lines.get(line)
                        if v_lines:
                            queue.extend([(v_line, length) for v_line in v_lines])
                            for v_line in v_lines:
                                # Add move count for this object
                                move_counts[v_line].append(length)
                        h_lines = vertical_attachement_h_lines.get(line)
                        if h_lines:
                            queue.extend([(h_line, length) for h_line in h_lines])
                            for h_line in h_lines:
                                # Add move count for this object
                                move_counts[h_line].append(length)
                break
                # Apply moves using the maximum count for each object
        for obj, counts in move_counts.items():
            if counts:
                max_move = max(counts)
                move_object(obj, 0, max_move, grid)
        # if _ == 1:
        #     plot_grids([input_grid, grid])
        input_grid = grid.copy()
    # process overlap corners
    if len(remove_colors) == 2: # TODO: remove colors simultaneously if they are in same length
        for x in range(grid.width):
            for y in range(1,grid.height):
                if grid.get(x, y) == grid.get(x + 1, y + 1):
                    grid[y][x+1]= grid[y][x]
                if grid.get(x, y) == grid.get(x - 1, y + 1):
                    grid[y][x-1]= grid[y][x]
    return grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py b6f77b65 remove_the_stick") 
