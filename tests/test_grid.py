
from arc_tools.grid import detect_objects
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
    objects = (grid, 4)
    assert len(objects) == 3, f"Expected 3 objects, got {len(objects)}"
    assert objects[0].region == GridRegion([GridPoint(0, 0), GridPoint(3, 3)])
    assert objects[1].region == GridRegion([GridPoint(4, 2), GridPoint(7, 5)])
    assert objects[2].region == GridRegion([GridPoint(0, 5), GridPoint(3, 8)])


def test_detect_objects():
    # TODO: Fix this test
    g=[[2, 2, 2, 2, 0], [2, 1, 5, 2, 0], [2, 8, 9, 0, 0], [2, 2, 0, 0, 0], [2, 0, 0, 0, 1]]
    grid = Grid(g)
    objs = detect_objects(grid,)
    print(len( objs))
    obj = objs[0]
    assert obj.region == GridRegion([GridPoint(0, 0), GridPoint(4, 4)]), f"Expected region {GridRegion([GridPoint(0, 0), GridPoint(4, 4)])}, got {obj.region}"
    # plot_grids([obj, grid], show=True)

if __name__ == "__main__":
    test_grid_with_hollow()
    test_find_4x4_boxes()
    test_detect_objects()
    print("All test cases passed")

