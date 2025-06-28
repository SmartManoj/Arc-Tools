from arc_tools import logger
from arc_tools.grid import Grid, detect_objects, Color, move_object, place_object_on_new_grid, GridRegion, GridPoint, SubGrid
from arc_tools.plot import plot_grids

def compare_boxes(key_box, find_box):
    if key_box.region.x1 == find_box.region.x1 and key_box.region.y1 == find_box.region.y1:
        return True
    for x in range(key_box.width):
        for y in range(key_box.height):
            if key_box.get(x, y) != find_box.get(x, y):
                return False
    return True

def highlight(box_idx, grid):
    col = box_idx % 4 * 5 + 1
    row = box_idx // 4 * 5 + 7 
    for x in range(col, col + 5):
        for y in range(row, row + 5):
            if grid.get(x, y) == grid.background_color:
                grid.set(x, y, Color.GREEN.value)

def highlight_the_box(grid: Grid) -> Grid:
    '''
    key_region = first 5 rows
    Highlight the box in the key_region using green color.
    If all highlighted boxes are in a straight line, then highlight outside the box using green color else red color.
    '''
    key_region = SubGrid(GridRegion([GridPoint(0, 0), GridPoint(grid.width - 1, 4)]), grid).get_full_grid()
    find_region = SubGrid(GridRegion([GridPoint(0, 6), GridPoint(grid.width - 1, grid.height - 4)]), grid).get_full_grid()
    key_boxes = detect_objects(key_region)
    find_boxes = detect_objects(find_region)
    idxs = []
    for key_box_idx, key_box in enumerate(key_boxes):
        for find_box_idx, find_box in enumerate(find_boxes):
            if compare_boxes(key_box, find_box):
                highlight(find_box_idx, grid)
                idxs.append(find_box_idx)
                break
    horizontal_line = all(idx // 4 == idxs[0] // 4 for idx in idxs)
    vertical_line = all(idx % 4 == idxs[0] % 4 for idx in idxs)
    success = horizontal_line or vertical_line
    for x in range(grid.width):
        if success:
            for y in list(range(5)):
                if grid.get(x, y) == grid.background_color:
                    grid.set(x, y, Color.GREEN.value)
        for y in list(range(grid.height-2,grid.height+1)):
            if grid.get(x, y) == grid.background_color:
                grid.set(x, y, Color.GREEN.value if success else Color.RED.value)
    return grid

if __name__ == "__main__":
    import os
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py d8e07eb2 highlight_the_box")

