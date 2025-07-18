import os
from collections import Counter
from arc_tools.grid import Grid, GridPoint, Color

def join_the_pipes(grid: Grid):

    def rotate_90_cw(m):
        if not m or not m[0]: return []
        return [list(i) for i in zip(*m[::-1])]

    def rotate_180(m):
        if not m or not m[0]: return []
        return [row[::-1] for row in m[::-1]]

    def rotate_90_ccw(m):
        if not m or not m[0]: return []
        return [list(i) for i in zip(*m)][::-1]

    def shrink_to_content(quad, bg_color):
        if not quad or not any(quad): return []
        min_r, max_r, min_c, max_c = -1, -1, float('inf'), -1
        for r, row in enumerate(quad):
            for c, val in enumerate(row):
                if val != bg_color:
                    if min_r == -1: min_r = r
                    max_r = r
                    min_c = min(min_c, c)
                    max_c = max(max_c, c)
        if min_r == -1: return []
        return [quad[r][min_c:max_c+1] for r in range(min_r, max_r+1)]

    def is_open_pipe(quad, bg_color):
        if not quad or not quad[0]: return False
        h, w = len(quad), len(quad[0])
        for r in range(h):
            if quad[r][0] != bg_color or quad[r][w-1] != bg_color:
                return True
        for c in range(w):
            if quad[0][c] != bg_color or quad[h-1][c] != bg_color:
                return True
        return False

    def get_alignment(sh, sw, name, is_pipe, canvas_dim=5):
        if is_pipe:
            start_r = (canvas_dim - sh) // 2
            if name == 'br':
                start_c = (canvas_dim - sw) // 2
            elif name in ['tl', 'bl']:
                start_c = 0
            else: # tr
                start_c = canvas_dim - sw
        else:
            start_r = (canvas_dim - sh) // 2
            start_c = (canvas_dim - sw) // 2
        return start_r, start_c

    def normalize_to_5x5(quad, bg_color, name, is_pipe):
        shrunk = shrink_to_content(quad, bg_color)
        canvas = [[bg_color] * 5 for _ in range(5)]
        if not shrunk or not shrunk[0]: return canvas
        
        sh, sw = len(shrunk), len(shrunk[0])
        start_r, start_c = get_alignment(sh, sw, name, is_pipe)
        
        for r in range(sh):
            for c in range(sw):
                if 0 <= start_r + r < 5 and 0 <= start_c + c < 5:
                    canvas[start_r + r][start_c + c] = shrunk[r][c]
        return canvas

    grid_data = [list(row) for row in grid]
    
    non_magenta_colors = [c for row in grid_data for c in row if c != Color.MAGENTA.value]
    bg_color = Counter(c for c in non_magenta_colors if c != 0).most_common(1)[0][0] if any(c != 0 for c in non_magenta_colors) else Color.BLACK.value

    magenta_points = [GridPoint(c, r) for r, row in enumerate(grid_data) for c, val in enumerate(row) if val == Color.MAGENTA.value]
    if not magenta_points: return grid
    
    center_y = Counter(p.y for p in magenta_points).most_common(1)[0][0]
    center_x = Counter(p.x for p in magenta_points).most_common(1)[0][0]

    h, w = len(grid_data), (len(grid_data[0]) if len(grid_data) > 0 else 0)

    quads = {
        'tl': [row[0:center_x] for row in grid_data[0:center_y]],
        'tr': [row[center_x+1:w] for row in grid_data[0:center_y]],
        'bl': [row[0:center_x] for row in grid_data[center_y+1:h]],
        'br': [row[center_x+1:w] for row in grid_data[center_y+1:h]],
    }

    stack_order = ['tl', 'br', 'tr', 'bl']
    
    final_pieces = []
    for name in stack_order:
        quad = quads[name]
        is_pipe = is_open_pipe(quad, bg_color)
        
        transformed_quad = quad
        if is_pipe:
            if name == 'tl': transformed_quad = rotate_90_cw(quad)
            elif name == 'tr': transformed_quad = rotate_90_ccw(quad)
            elif name == 'bl': transformed_quad = rotate_180(quad)
        
        normalized = normalize_to_5x5(transformed_quad, bg_color, name, is_pipe)
        final_pieces.append(normalized)

    output_grid_data = []
    for i, piece in enumerate(final_pieces):
        output_grid_data.extend(piece)
        if i < len(final_pieces) - 1:
            output_grid_data.append([Color.MAGENTA.value] * 5)

    return Grid(output_grid_data, background_color=bg_color)

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 78332cb0 join_the_pipes")
