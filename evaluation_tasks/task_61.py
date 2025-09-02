import os
from arc_tools import plot
from arc_tools.grid import Grid, detect_objects, move_object, place_object
from arc_tools import logger
from arc_tools.plot import plot_grids

def magnetic_nets(grid: Grid):
    '''
    Transform grid by placing layer of each objects at the bottom of each colored section and replacing them with corner columns.
    '''
    all_objects = detect_objects(grid)
    nets = []
    objects = []
    for object in all_objects:
        if object.width == grid.width:
            nets.append(object)
        else:
            objects.append(object)
    for object in objects:
        layers = detect_objects(object, single_color_only=1)
        for layer in layers:
            # Find the correct net based on the object's color
            layer_color = layer.color
            for net in nets:
                if net[1][1] == layer_color:
                    target_net = net
                    break
            
            layer = layer.replace_color(layer_color, target_net[0][0], replace_in_parent_grid=False)
            place_object(layer, layer.region.x1, target_net.region.y2 - layer.height + 1, grid)
        
        
    return grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 7c66cb00 magnetic_nets") 
