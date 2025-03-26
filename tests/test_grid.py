
from arc_tools.grid import detect_objects


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
    assert detect_objects(grid_with_hollow)[0].has_hollow_space() == True
    assert detect_objects(grid_without_hollow)[0].has_hollow_space() == False


if __name__ == "__main__":
    test_grid_with_hollow()
    print("All test cases passed")
