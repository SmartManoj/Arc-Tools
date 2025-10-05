import os
from arc_tools.grid import Grid, copy_object, detect_objects, Color
from arc_tools import logger

def good_will_win(grid: Grid):
    '''
    transfer lives from red plate to green blate
    '''
    objects = detect_objects(grid)
    lives = []
    red_plates = []
    for obj in objects:
        if obj.color == Color.RED.value and obj.height == 1:
            red_plates.append(obj)
        elif obj.color == Color.GREEN.value and obj.height == 1:
            green_plate = obj
        else:
            lives.append(obj)
    
    red_lives = 0
    for life in lives:
        if any(life.region.x1 == red_plate.region.x1 for red_plate in red_plates):
            life.replace_all_color(Color.GRAY, in_place=True)
            red_lives += 1
    for life in lives:
        if life.region.x1 == green_plate.region.x1:
            for i in range(red_lives):
                copy_object(life, 0, - (life.height + 1) * (i + 1),  grid)
            break
    
    # remove plates
    grid.remove_objects([green_plate] + red_plates)
    return grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py 9aaea919 good_will_win") 
