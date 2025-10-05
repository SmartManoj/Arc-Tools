import os

from numpy import append
from arc_tools.grid import Grid, detect_objects, Color
from arc_tools import logger
from arc_tools.plot import plot_grids

def long_live_connections(grid: Grid):
    '''
    only show objects connected with gray line
    '''
    objects = detect_objects(grid, ignore_colors=[Color.GRAY.value], go_diagonal=0)
    gray_line = detect_objects(grid, required_color=Color.GRAY.value)[0]
    gray_end_points = []
    for p in gray_line.points:
        all_points = [p for p in grid.get_surrounding_points(row=p.y, col=p.x) if p.value == Color.GRAY.value]
        center_points = [p for p in grid.get_surrounding_points(row=p.y, col=p.x, only_edge_center=True) if p.value == Color.GRAY.value]
        corner_points = [p for p in all_points if p not in center_points]
        if len(corner_points) < 2 and len(center_points) < 2:
            if len(corner_points)==1 and len(center_points)==1:
                if center_points[0] not in grid.get_surrounding_points(row=corner_points[0].y, col=corner_points[0].x):
                    continue
            gray_end_points.append(p)
    # plot_grids(objects)
    outer_inner_map = {}
    for obj in objects:
        bp = obj.get_border_points()
        outer_inner_map[obj.get_border_points()[0].value] = obj[1][1]
    for obj in objects:
        # get surrounding points
        edge_center_surrounding_points = [p for p in obj.get_surrounding_points(only_edge_center=True) if p.value == Color.GRAY.value]
        valid_gray_points = []
        for p in edge_center_surrounding_points:
            if p in gray_end_points:
                valid_gray_points.append(p)
        if not valid_gray_points or len(edge_center_surrounding_points) == 4:
            grid.remove_object(obj)
        else:
            v = outer_inner_map.get(grid[obj.region.y1+1][obj.region.x1+1])
            if v:
                grid[obj.region.y1+1][obj.region.x1+1] = v
    return grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py d35bdbdc long_live_connections") 
