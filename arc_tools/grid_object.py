class GridPoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __str__(self):
        return f"({self.x}, {self.y})"

class GridRegion:
    def __init__(self, points: list[GridPoint]):
        self.points = points

    def __str__(self):
        return f"[{', '.join(str(point) for point in self.points)}]"

class GridObject:
    def __init__(self, region: GridRegion):
        self.region = region # Keep the attribute name 'region' for consistency

    def __str__(self):
        return f"Region: {self.region}"

import numpy as np
from collections import deque

def detect_objects(grid) -> list[GridObject]:
    grid_np = np.array(grid)
    rows, cols = grid_np.shape
    visited = np.zeros_like(grid_np, dtype=bool)
    objects = []

    for r in range(rows):
        for c in range(cols):
            if grid_np[r, c] != 0 and not visited[r, c]:
                # Start BFS for a new object
                current_object_points = []
                q = deque([(r, c)])
                visited[r, c] = True

                while q:
                    row, col = q.popleft()
                    current_object_points.append(GridPoint(col, row)) # x=col, y=row

                    # Check neighbors (4-connectivity: up, down, left, right)
                    for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                        nr, nc = row + dr, col + dc
                        if 0 <= nr < rows and 0 <= nc < cols and \
                           grid_np[nr, nc] != 0 and not visited[nr, nc]:
                            visited[nr, nc] = True
                            q.append((nr, nc))
                
                if current_object_points:
                    objects.append(GridObject(GridRegion(current_object_points)))

    return objects
    

def move_object(object_to_move: GridObject, x: int, y: int, grid) -> list[list[int]]:
    grid_np = np.array(grid)
    rows, cols = grid_np.shape
    new_grid = np.zeros_like(grid_np)
    
    all_objects = detect_objects(grid) # Detect all objects first
    
    # Create a set of points for the object to move for efficient comparison
    object_to_move_points_set = set((p.x, p.y) for p in object_to_move.region.points)

    moved_object_placed = False # Flag to ensure the target object is processed

    for current_object in all_objects:
        current_object_points_set = set((p.x, p.y) for p in current_object.region.points)
        
        # Check if this is the object we need to move by comparing point sets
        is_object_to_move = (current_object_points_set == object_to_move_points_set)

        if is_object_to_move:
            moved_object_placed = True
            if not current_object.region.points:
                continue # Skip if the object to move is empty

            # Find the top-left corner of the object to move
            min_x = min(p.x for p in current_object.region.points)
            min_y = min(p.y for p in current_object.region.points)

            # Calculate the offset to move the top-left corner to (x, y)
            offset_x = x - min_x
            offset_y = y - min_y

            # Move each point of the target object
            for point in current_object.region.points:
                original_value = grid_np[point.y, point.x]
                new_x = point.x + offset_x
                new_y = point.y + offset_y

                # Place the value in the new grid if within bounds
                if 0 <= new_y < rows and 0 <= new_x < cols:
                    # Avoid overwriting parts of other objects already placed
                    if new_grid[new_y, new_x] == 0:
                         new_grid[new_y, new_x] = original_value
                    # else: Handle collision? For now, first object placed wins.
        else:
            # Keep other objects in their original place
            for point in current_object.region.points:
                 # Place the value in the new grid if within bounds
                 if 0 <= point.y < rows and 0 <= point.x < cols:
                     # Avoid overwriting parts of the moved object
                     if new_grid[point.y, point.x] == 0:
                          new_grid[point.y, point.x] = grid_np[point.y, point.x]
                     # else: Handle collision? For now, first object placed wins.

    # Sanity check: If the object to move wasn't found among detected objects (e.g., empty grid input)
    if not moved_object_placed and object_to_move.region.points:
         # Apply the move logic directly if the object wasn't part of the detected set
         # This handles cases where object_to_move might be constructed externally
         min_x = min(p.x for p in object_to_move.region.points)
         min_y = min(p.y for p in object_to_move.region.points)
         offset_x = x - min_x
         offset_y = y - min_y
         for point in object_to_move.region.points:
             original_value = grid_np[point.y, point.x] # Need original grid value
             new_x = point.x + offset_x
             new_y = point.y + offset_y
             if 0 <= new_y < rows and 0 <= new_x < cols:
                 if new_grid[new_y, new_x] == 0:
                     new_grid[new_y, new_x] = original_value


    return new_grid.tolist() # Return as list of lists
