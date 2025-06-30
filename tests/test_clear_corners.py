from arc_tools.grid import Grid, GridPoint, GridRegion, SubGrid
from arc_tools.plot import plot_grid

a = [
    [1, 2, 3, 4, 5],
    [6, 7, 8, 9, 10],
    [11, 12, 13, 14, 15],
    [16, 17, 18, 19, 20],
    [21, 22, 23, 24, 25]
]


expected = [
    [0, 0, 3, 0, 0],
    [0, 0, 8, 0, 0],
    [11, 12, 13, 14, 15],
    [0, 0, 18, 0, 0],
    [0, 0, 23, 0, 0]
]


subgrid = SubGrid(GridRegion([GridPoint(0, 1), GridPoint(0, 3)]), Grid(a))

expanded_subgrid_by_2 = [
    [1, 2, 3, 0, 0],
    [6, 7, 8, 0, 0],
    [11, 12, 13, 0, 0],
    [16, 17, 18, 0, 0],
    [21, 22, 23, 0, 0],
]


expected_2 = [
    [1, 0, 0, 0, 0],
    [6, 7, 8, 0, 0],
    [11, 12, 13, 0, 0],
    [16, 17, 18, 0, 0],
    [21, 0, 0, 0, 0],
]



assert (Grid([row[:] for row in a]).clear_corners(grid_size=2) == Grid(expected))
assert (Grid([row[:] for row in expanded_subgrid_by_2]).clear_corners(grid_size=2, relative_to=subgrid) == Grid(expected_2))
