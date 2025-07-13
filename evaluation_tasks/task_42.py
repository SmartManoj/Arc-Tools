import os
from arc_tools.grid import Color, Grid, detect_objects

def counter_box(grid: Grid):
    '''
    Finds a black box object in the input grid, identifies the colors within it,
    counts objects of those colors outside the box, and creates an output grid showing the counts.
    
    Algorithm:
    1. Detects the first black object in the grid using detect_objects()
    2. Extracts all unique colors from within this black box region (excluding black itself)
    3. Counts the number of distinct objects of each color that exist outside the black box
    4. Creates an output grid with the same dimensions as the black box
    5. Displays the counts by placing colored pixels in a grid pattern:
       - Each color gets its own row (rows 1, 3, 5, etc.)
       - Count is shown as spaced pixels (columns 1, 3, 5, etc.)
       - Black pixels fill the remaining spaces
    
    Returns:
        Grid: Output grid showing color counts in the black box format
    '''
    black_box = detect_objects(grid, required_color=Color.BLACK)[0]
    # Get colors inside the black box (excluding black itself) in the order they appear
    colors_in_box = black_box.get_unique_values()
    colors_in_box.remove(Color.BLACK.value)
    
    # Count occurrences of each color outside the black box by counting objects
    color_counts = {}
    
    # Create a copy of the grid with the black box region removed (set to background)
    grid_copy = grid.copy()
    for y in range(black_box.region.y1, black_box.region.y2 + 1):
        for x in range(black_box.region.x1, black_box.region.x2 + 1):
            grid_copy.set(x, y, grid.background_color)
    
    # Count objects of each color in the modified grid
    for color in colors_in_box:
        color_enum = Color(color)
        objects = detect_objects(grid_copy, required_color=color_enum)
        color_counts[color] = len(objects)
    
    # Create output grid with the same dimensions as the black box
    box_width = black_box.region.x2 - black_box.region.x1 + 1
    box_height = black_box.region.y2 - black_box.region.y1 + 1
    
    # Create 2D list filled with black color
    output_data = [[Color.BLACK.value for _ in range(box_width)] for _ in range(box_height)]
    output_grid = Grid(output_data, Color.BLACK.value)
    
    # Place colors in specific rows with their counts
    for i, color in enumerate(colors_in_box):
        row = i * 2 + 1  # Use rows 1, 3, 5, ... (skip row 0)
        count = color_counts[color]
        for j in range(count):
            col = j * 2 + 1  # Use columns 1, 3, 5, ... (skip column 0)
            if row < box_height and col < box_width:
                output_grid.set(col, row, color)
    
    return output_grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 58490d8a counter_box") 
