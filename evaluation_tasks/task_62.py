import os
from arc_tools.grid import BorderSide, Color, Grid, detect_objects, place_object
from arc_tools import logger
from arc_tools.plot import plot_grids

def mirror_it(grid: Grid):
    '''
    Transform shapes based on their position and orientation:
    - If first point is red, mirror NW
    - If it is last, then SE  
    - If vertical or horizontal add opposite side
    '''
    objects = detect_objects(grid)
    result_grid = grid.copy()

    # Process each object
    for obj in objects:
        red_count = obj.get_values_count()[Color.RED.value]
        # log red count
        if red_count != 1:
            # check which border is red
            if  all(i == Color.RED.value for i in obj.get_edge_data(BorderSide.TOP)):
                # mirror up
                new_obj = obj.flip_horizontally()
                place_object(new_obj, obj.region.x1, obj.region.y1-obj.height + 1, result_grid, remove_object=False)
            elif  all(i == Color.RED.value for i in obj.get_edge_data(BorderSide.BOTTOM)):
                new_obj = obj.flip_horizontally()
                place_object(new_obj, obj.region.x1, obj.region.y1+obj.height - 1, result_grid, remove_object=False)
            elif  all(i == Color.RED.value for i in obj.get_edge_data(BorderSide.LEFT)):
                new_obj = obj.flip_vertically()
                place_object(new_obj, obj.region.x1-obj.width + 1, obj.region.y1, result_grid, remove_object=False)
            elif  all(i == Color.RED.value for i in obj.get_edge_data(BorderSide.RIGHT)):
                new_obj = obj.flip_vertically()
                place_object(new_obj, obj.region.x1+obj.width - 1, obj.region.y1, result_grid, remove_object=False)
            
        else:
            if obj[0][0] == Color.RED.value:
                new_obj = obj.flip_horizontally()
                new_obj = new_obj.flip_vertically()
                place_object(new_obj, obj.region.x1 - obj.width + 1, obj.region.y1-obj.height + 1, result_grid, remove_object=False)
            elif obj[0][obj.width-1] == Color.RED.value:
                new_obj = obj.flip_horizontally()
                new_obj = new_obj.flip_vertically()
                place_object(new_obj, obj.region.x1 + obj.width - 1, obj.region.y1-obj.height + 1, result_grid, remove_object=False)
            elif obj[obj.height-1][0] == Color.RED.value:
                new_obj = obj.flip_horizontally()
                new_obj = new_obj.flip_vertically()
                place_object(new_obj, obj.region.x1 - obj.width + 1, obj.region.y2, result_grid, remove_object=False)
            elif obj[obj.width-1][obj.height-1] == Color.RED.value:
                new_obj = obj.flip_horizontally()
                new_obj = new_obj.flip_vertically()
                place_object(new_obj, obj.region.x1 + obj.width - 1, obj.region.y1+obj.height - 1, result_grid, remove_object=False)

    return result_grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 7ed72f31 mirror_it") 
