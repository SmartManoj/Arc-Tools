from arc_tools.grid import Grid
from arc_tools.plot import plot_grid
from task_4 import shoot_light

def test_shoot_light():
    # Create a test grid with L-shaped objects and target objects
    test_grid = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 2, 0],
        [0, 0, 0, 0, 0, 0, 2, 0],
    ]
    
    grid = Grid(test_grid)
    plot_grid(grid, name="input.png", show=True)
    
    result = shoot_light(grid)
    plot_grid(result, name="output.png", show=True)
    
    # Expected output should have:
    # 1. Yellow light path from L-shape
    # 2. Red light path after hitting the red object
    expected = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 0, 0, 0, 0, 0],
        [0, 1, 4, 4, 4, 4, 4, 4],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 2, 0],
        [0, 0, 0, 0, 0, 0, 2, 0],
    ]
    
    assert result == Grid(expected), "Test failed: Output does not match expected result"

if __name__ == "__main__":
    test_shoot_light() 