import os
from arc_tools.grid import Color, Grid, SubGrid, GridRegion, GridPoint

def detect_rectangular_frames(grid: Grid) -> list[SubGrid]:
    '''
    check the right dot and the bottom dot(to find the correct corner) and go on until it is not the same color.
    then check the bottom dot and go on until it is not the same color.
    then check the left dot and go on until it is not the same color.
    then check the top dot and go on until the initial dot is reached.
    if it is the same color, then it is a rectangular fram.
    if it is not the same color, then it is not a rectangular fram.
    return the rectangular frames.
    '''
    frames = []
    for row in range(grid.height):
        for col in range(grid.width):
            actual_left = col
            actual_up = row
            actual_down = actual_right  = None 
            current_color = grid[row][col]
            if current_color == Color.BLACK.value:
                continue
            for right in range(actual_left, grid.width - 1):
                if grid[actual_up+1][right] == current_color:
                    actual_right = right
                if grid[actual_up][right+1] != current_color:
                    break
            is_not_rectangular =  not actual_right or actual_left >= actual_right - 1
            if is_not_rectangular :
                continue
            for down in range(actual_up, grid.height - 1):
                if grid[down][actual_right-1] == current_color:
                    actual_down = down
                if grid[down+1][actual_right] != current_color:
                    break
            is_not_rectangular = not actual_down or actual_up >= actual_down - 1
            if is_not_rectangular:
                continue
            
            for left in range(actual_right, actual_left-1, -1):
                if grid[actual_down][left-1] != current_color:
                    break
            is_not_rectangular = left != actual_left
            if is_not_rectangular:
                continue
            for up in range(actual_down, actual_up-1, -1):
                if grid[up-1][actual_left] != current_color:
                    break
            is_not_rectangular = up != actual_up
            if is_not_rectangular:
                continue
            frames.append(SubGrid(GridRegion((GridPoint(actual_left, actual_up), GridPoint(actual_right, actual_down))), grid,))
    return frames
def replicate(grid: Grid) -> Grid:
    '''
    find two large frames and four small frames
    each larger frame contains two smaller frame
    '''
    new_grid = grid.copy()
    new_grid.background_color = -1
    frames = detect_rectangular_frames(new_grid)

    # sort the frames by the area
    frames.sort(key=lambda x: x.area(), reverse=True)
    large_frames = frames[:2]
    small_frames = frames[2:6]
    # remove the border from small frames
    small_frames = [frame.remove_border() for frame in small_frames]
    hollow_frame = next(frame for frame in small_frames if frame.get_total_unique_dots() == 1)
    # hollow_frame sibling
    for frame in large_frames:
        if frame.contains(hollow_frame):
            hollow_frame_grid = frame
            break
    for frame in small_frames:
        if frame == hollow_frame:
            continue
        if hollow_frame_grid.contains(frame):
            hollow_frame_sibling = frame
            break
    # set background color to 0 for small frames
    for frame in small_frames:
        frame.background_color = 0
    complete_frames = [f for f in small_frames if f not in [hollow_frame, hollow_frame_sibling]]
    dense_complete_frame, sparse_complete_frame  = sorted(complete_frames, key=lambda x: x.get_total_dots(), reverse=True)
    sparse_complete_frame_copy = sparse_complete_frame.copy()
    def join_dots(frame: SubGrid):
        dots = []
        dot_color = None
        for r in range(frame.height):
            for c in range(frame.width):
                color = frame[r][c]
                if color != frame.background_color:
                    dots.append(GridPoint(c, r))
                    dot_color = color
        if dots:
            for i in range(len(dots)):
                for j in range(i + 1, len(dots)):
                    p1 = dots[i]
                    p2 = dots[j]

                    if p1.y == p2.y:
                        for x in range(min(p1.x, p2.x), max(p1.x, p2.x) + 1):
                            if frame[p1.y][x] == frame.background_color:
                                frame[p1.y][x] = dot_color

                    if p1.x == p2.x:
                        for y in range(min(p1.y, p2.y), max(p1.y, p2.y) + 1):
                            if frame[y][p1.x] == frame.background_color:
                                frame[y][p1.x] = dot_color
    
    def invert_dots(frame: SubGrid):
        frame_colors = frame.get_unique_values()
        total_colors = len(frame_colors)
        for r in range(frame.height):
            for c in range(frame.width):
                if frame[r][c] != frame.background_color:
                    frame[r][c] = frame.background_color
                else:
                    frame[r][c] = frame_colors[(r * frame.width + c + 1) % total_colors]
    
    def copy_corner_and_fill_frame(frame: SubGrid):
        corners_and_directions = [
            ((0, 0), (1, 1)),
            ((frame.width - 1, 0), (-1, 1)),
            ((0, frame.height - 1), (1, -1)),
            ((frame.width - 1, frame.height - 1), (-1, -1)),
        ]
        for (corners, direction) in corners_and_directions:
            corner_plus_one = corners[0] + direction[0], corners[1] + direction[1]
            corner_color = frame[corner_plus_one[0]][corner_plus_one[1]]
            if corner_color != frame.background_color:
                adjacent_color = frame[corners[0] + direction[0]][corners[1]]
                break
        # apply the same to other corners
        for (corners, direction) in corners_and_directions:
            corner_plus_one = corners[0] + direction[0], corners[1] + direction[1]
            frame[corner_plus_one[0]][corner_plus_one[1]] = corner_color
            frame[corners[0] + direction[0]][corners[1]] = adjacent_color
            frame[corners[0]][corners[1] + direction[1]] = adjacent_color
        # set corner color to remaining aread except the corner 2*2 grid
        for r in range(frame.height):
            for c in range(frame.width):
                if r < 2 and c < 2 or r < 2 and c > frame.width - 3 or r > frame.height - 3 and c < 2 or r > frame.height - 3 and c > frame.width - 3:
                    continue
                frame[r][c] = corner_color
        
        return frame

    # these functions are generated based on dense complete frame
    function_lists = [join_dots, invert_dots, copy_corner_and_fill_frame]
    for function in function_lists:
        function(sparse_complete_frame)
        if sparse_complete_frame.compare(dense_complete_frame):
            break
    hollow_frame = hollow_frame_sibling.copy()
    function(hollow_frame)

    # apply the changes between the complete frames to the hollow frame
    # plot_grids([sparse_complete_frame, dense_complete_frame,  hollow_frame_sibling], titles=["Sparse Complete Frame", "Dense Complete Frame", "Hollow Frame Sibling"])
    return hollow_frame

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 4c7dc4dd replicate")
