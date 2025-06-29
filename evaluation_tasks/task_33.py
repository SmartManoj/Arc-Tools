import os
from collections import Counter
from arc_tools.grid import Color, Grid, SubGrid, detect_objects, GridRegion, GridPoint, place_object_on_new_grid

def build_a_box(grid: Grid):
    """
    Transforms a grid of horizontal stripes into a grid of concentric squares.

    The transformation follows these rules:
    1. The sequence of colored horizontal stripes from top to bottom in the input grid
       corresponds to the sequence of concentric frames from the outside to the inside
       of the output grid.
    2. The height of each stripe in the input grid determines the thickness of the
       corresponding frame in the output grid.
    3. The output grid's dimensions are calculated as `2 * H - 2`, where `H` is the
       height of the input grid.
    4. The transformation process involves drawing a series of filled, colored rectangles,
       starting from the outermost frame and working inwards. Each new, smaller
       rectangle is drawn on top of the previous one.
    """
    # 1. Identify stripes from the input grid
    stripes = []
    # Start with the first row as the first stripe
    stripes.append({'color': grid[0][0], 'height': 1})
    for r in range(1, grid.height):
        row_color = grid[r][0]
        # If the color is the same as the last stripe, increment its height
        if row_color == stripes[-1]['color']:
            stripes[-1]['height'] += 1
        # Otherwise, start a new stripe
        else:
            stripes.append({'color': row_color, 'height': 1})

    # 2. Calculate output dimensions based on the cumulative thickness of stripes
    output_height = 2 * grid.height - 2
    output_width = 2 * grid.height - 2

    output_grid = Grid([[Color.BLACK.value for _ in range(output_width)] for _ in range(output_height)])

    # 3. Construct concentric rectangles
    offset = 0
    for stripe in stripes:
        color = stripe['color']
        thickness = stripe['height']

        for r in range(offset, output_height - offset):
            for c in range(offset, output_width - offset):
                output_grid[r][c] = color
        
        offset += thickness

    return output_grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 45a5af55 build_a_box")
