from arc_tools.grid import detect_objects, split_into_square_boxes, move_object
from arc_tools.grid import Grid, GridRegion, GridPoint
from arc_tools.plot import plot_grids
def test_grid_with_hollow():
    grid_with_hollow = [
        [0, 0, 1, 0, 0],
        [0, 1, 1, 1, 0],
        [0, 1, 0, 1, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 0, 0, 0],
    ]
    grid_without_hollow = [
        [0, 0, 1, 0, 0],
        [0, 1, 1, 1, 0],
        [0, 1, 1, 1, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 0, 0, 0],
    ]
    assert detect_objects(Grid(grid_with_hollow))[0].has_hollow_space() == True
    assert detect_objects(Grid(grid_without_hollow))[0].has_hollow_space() == False



def test_split_into_square_boxes():
    # Example grid with one 4x4 box
    grid = [
        [1, 1, 1, 1, 0, 0, 0, 0],
        [1, 2, 2, 1, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [0, 0, 0, 0, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 0, 0, 0, 0],
        [1, 1, 1, 1, 0, 0, 0, 0],
        [1, 1, 1, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ]
    grid = Grid(grid)
    objects = split_into_square_boxes(grid, 4)
    assert len(objects) == 3, f"Expected 3 objects, got {len(objects)}"
    assert objects[0].region == GridRegion([GridPoint(0, 0), GridPoint(3, 3)])
    assert objects[1].region == GridRegion([GridPoint(4, 2), GridPoint(7, 5)])
    assert objects[2].region == GridRegion([GridPoint(0, 5), GridPoint(3, 8)])


def test_detect_objects():
    g=[[2, 2, 2, 2, 0], [2, 1, 5, 2, 0], [2, 8, 9, 0, 0], [2, 2, 0, 0, 0], [2, 0, 0, 0, 1]]
    grid = Grid(g)
    objs = detect_objects(grid,)
    print(len( objs))
    obj = objs[0]
    expected_region = GridRegion([GridPoint(0, 0), GridPoint(3, 4)])
    assert obj.region == expected_region, f"Expected region {expected_region}, got {obj.region}"

def test_detect_objects_single_color():
    grid = [
        [0, 1, 0, 2, 0],
        [1, 1, 2, 2, 0],
        [0, 2, 0, 0, 0],
        [2, 2, 0, 0, 0],
    ]
    grid = Grid(grid)
    objs = detect_objects(grid, single_color_only=True, go_diagonal=False)
    expected_regions = [
        GridRegion([GridPoint(0, 0), GridPoint(1, 1)]),
        GridRegion([GridPoint(2, 0), GridPoint(3, 1)]),
        GridRegion([GridPoint(0, 2), GridPoint(1, 3)]),
    ]
    for obj, expected_region in zip(objs, expected_regions):
        assert obj.region == expected_region, f"Expected region {expected_region}, got {obj.region}"
    assert len(objs) == 3, f"Expected 3 objects, got {len(objs)}"

def test_move_object():
    # Create a test grid with a simple object
    grid = [
        [0, 0, 0, 0, 0],
        [0, 1, 1, 1, 0],
        [0, 1, 0, 1, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 0, 0, 0],
    ]
    grid = Grid(grid)
    initial_grid = grid.copy()
    # Detect the object in the grid
    objects = detect_objects(grid)
    assert len(objects) == 1, "Expected one object in the grid"
    original_obj = objects[0]
    
    # Copy the object to a new position (1 unit right, 1 unit down)
    dx, dy = 1, 0
    moved_obj = move_object(original_obj, dx, dy, grid)
    
    # Verify the copied object's region is correct
    expected_region = GridRegion([
        GridPoint(original_obj.region.x1 + dx, original_obj.region.y1 + dy),
        GridPoint(original_obj.region.x2 + dx, original_obj.region.y2 + dy)
    ])
    grid.display()
    return
    assert moved_obj.region == expected_region, f"Expected region {expected_region}, got {moved_obj.region}"
    
    # Verify the grid has the copied object
    for row in range(moved_obj.height):
        for col in range(moved_obj.width):
            if original_obj[row][col] != grid.background_color:
                assert grid[row + dy][col + dx] == original_obj[row][col], \
                    f"Expected value {original_obj[row][col]} at position ({col + dx}, {row + dy})"
    grid.display()
    plot_grids([initial_grid, grid], show=True)

if __name__ == "__main__":
    test_grid_with_hollow()
    test_split_into_square_boxes()
    test_detect_objects()
    test_detect_objects_single_color()
    test_move_object()
    print("All test cases passed")

