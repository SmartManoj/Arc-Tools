from collections import defaultdict
import os

from arc_tools import plot
from arc_tools.grid import Grid, detect_objects
from arc_tools import logger
from arc_tools.plot import plot_grids

def energy_bars(grid: Grid):
    '''
    Energy bars at top. Poles at bottom.
    Change the pole depends upon the energy bar height.
    1 = make the longest solid
    2 = make the medium solid
    3 = make the shortest solid
    '''
    objects = detect_objects(grid, width=1)
    energy_bars = []
    poles = []
    poles_by_color = defaultdict(list)
    for obj in objects:
        if obj.region.y2 == grid.height - 1:
            poles.append(obj)
            poles_by_color[obj[0][0]].append(obj)
        else:
            energy_bars.append(obj)
    energy_bar_types = {
        1: 'long',
        2: 'medium',
        3: 'small',
    }
    for i, energy_bar in enumerate(energy_bars):
        energy_bar_type = energy_bar_types[energy_bar.height]

        pole_group = poles_by_color[energy_bar.color]
        pole_group.sort(key=lambda x: x.height)
        if energy_bar_type == 'long':
            required_pole = pole_group[-1]
        elif energy_bar_type == 'medium':
            required_pole = pole_group[-2]
        elif energy_bar_type == 'small':
            required_pole = pole_group[-3]
        for x, y in required_pole.points:
            grid[y][x] = energy_bar.color

    return grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 97d7923e energy_bars") 
