import json


d = [[0, 0, 0, 0, 0, 0, 0], [0, 8, 8, 8, 8, 8, 0], [0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 6, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0], [0, 6, 6, 6, 6, 6, 0], [0, 0, 0, 0, 0, 0, 0]]
d = json.load(open("grid1.json"))
from arc_tools.grid import Grid, detect_objects, GridRegion, GridPoint
from arc_tools.plot import plot_grids
from main import merge_nearby_objects_as_square 
d = Grid(d)
for i in range(0,22):
    for j in range(0,30):
        d[i][j] = 0
objs = detect_objects(d)
print('Before merge')
print(len(objs))
for i in range(len(objs)):
    print(objs[i].region)
objs = merge_nearby_objects_as_square(objs,0)

# d.save()
print('After merge')
print(len(objs))
for i in range(len(objs)):
    print(objs[i].region)

# plot_grids([d,*objs], show=1  )
# assert region 1,1 to 5,5 is 1
# assert objs[0].region == GridRegion([GridPoint(1, 1), GridPoint(5, 5)]), f"Region is {objs[0].region}"
