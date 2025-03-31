

90 b5ca7ac4
boxe shape  5x5?
1. move light blue box to left wall
2. move red box to right wall
---

99 cbebaa4b
1. orange dot is the min value of the object.
2. yellow is the centre object? (or no hollow object with no orange dot at corners) or both?
3. move other objects to the yellow object by matching with the dot .
---

111 e3721c99
divider line - vertically, horizontally, or L-shaped (top left?) 
1. extract hollow counts of the objects from the smaller grid
2. change the object color according to the hollow count, if hollow count is not found, then remove the object
---

117 f560132c
jigsaw puzzle
find output grid size by counting the number of objects in the input grid
1. find color map box
2. piece that having the color map box is the first piece without rotation.
3. move the jigsaw puzzle pieces to the correct position (do largest piece first)
4. replace colors of the objects in the output grid with the color map
---

118 f931b4a8
input grid: divide the grid into 4 subgrids 
first piece: row
second piece: col
third piece: background color (ratio map)
fourth piece: data

output grid: A grid with row, col, and data else background color (ratio map).

