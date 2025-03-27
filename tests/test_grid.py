
from arc_tools.grid import detect_objects
from arc_tools.grid import find_square_boxes
from arc_tools.grid import Grid, GridRegion, GridPoint
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



def test_find_4x4_boxes():
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
    print(grid.background_color)
    objects = find_square_boxes(grid, 4)
    assert len(objects) == 3, f"Expected 3 objects, got {len(objects)}"
    assert objects[0].region == GridRegion([GridPoint(0, 0), GridPoint(3, 3)])
    assert objects[1].region == GridRegion([GridPoint(4, 2), GridPoint(7, 5)])
    assert objects[2].region == GridRegion([GridPoint(0, 5), GridPoint(3, 8)])


if __name__ == "__main__":
    test_grid_with_hollow()
    test_find_4x4_boxes()
    print("All test cases passed")

