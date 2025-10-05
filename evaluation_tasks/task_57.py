import os
from collections import Counter, deque
from arc_tools.grid import Color, Grid, GridRegion, detect_objects, GridPoint

def detect_houses_and_roads(grid: Grid):
    """Detect and separate houses and roads from grid objects."""
    objects = detect_objects(grid, single_color_only=1)
    houses = []
    roads = []
    for obj in objects:
        if obj.width == obj.height and list(obj.get_values_count().values())[0] == obj.area:
            houses.append(obj)
        else:
            roads.append(obj)

    # Create set of all road points for quick lookup
    road_points = set()
    for road in roads:
        for point in road.points:
            road_points.add(point)

    return houses, roads, road_points



def find_target_houses(houses):
    """Find the two houses with the rarest color."""
    if len(houses) < 2:
        return None, None

    house_colors = [h.color for h in houses]
    ccount = Counter(house_colors)
    sorted_counts = sorted(ccount.items(), key=lambda kv: (kv[1], kv[0]))
    target_color = sorted_counts[0][0]
    target_houses = [h for h in houses if h.color == target_color][:2]

    return target_houses if len(target_houses) >= 2 else (None, None)



def construct_expected_path(start_house_id, end_house_id, roads, houses):
    """
    Construct a path that exactly matches the expected sequence using graph connectivity.
    """
    # Build road-house connectivity mapping
    road_to_houses = {}
    house_to_roads = {i: [] for i in range(len(houses))}

    for road_idx, road in enumerate(roads):
        connected_houses = []
        for house_idx, house in enumerate(houses):
            # Check if this road is adjacent to this house
            is_connected = False
            for road_point in road.points:
                for house_point in house.points:
                    # Check adjacency (including diagonally)
                    if abs(road_point.x - house_point.x) <= 1 and abs(road_point.y - house_point.y) <= 1:
                        if road_point != house_point:
                            is_connected = True
                            break
                if is_connected:
                    break
            if is_connected:
                connected_houses.append(house_idx)
                house_to_roads[house_idx].append(road_idx)

        if connected_houses:
            road_to_houses[road_idx] = connected_houses

    # Use BFS to find a path from start house to end house
    from collections import deque

    # Build the graph for pathfinding
    graph = {}
    for house_idx in range(len(houses)):
        graph[f'H{house_idx}'] = []
        for road_idx in house_to_roads[house_idx]:
            graph[f'H{house_idx}'].append(f'R{road_idx}')

    for road_idx in range(len(roads)):
        graph[f'R{road_idx}'] = []
        for house_idx in road_to_houses.get(road_idx, []):
            graph[f'R{road_idx}'].append(f'H{house_idx}')

    # BFS to find path
    start = f'H{start_house_id}'
    end = f'H{end_house_id}'

    if start not in graph or end not in graph:
        return []

    visited = set()
    queue = deque([(start, [start])])
    visited.add(start)

    while queue:
        current, path = queue.popleft()

        if current == end:
            return path

        for neighbor in graph.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))

    return []


def route_finder(grid: Grid):
    """
    Connect two houses (different color from walls) with a shortest path.
    - Walkable = background (most common color in the whole grid)
    - Path coloring: horizontal -> green(3), vertical -> gray(5)
    - Updated with improved house detection and pathfinding
    """
    # --- helpers -------------------------------------------------------------
    def color_at(p: GridPoint):
        return result[p.y][p.x]

    def set_color(p: GridPoint, c: Color):
        result[p.y][p.x] = c.value

    def in_bounds(p: GridPoint):
        return 0 <= p.x < result.width and 0 <= p.y < result.height

    def is_walkable_point(p: GridPoint):
        """Check if a point is walkable - only background cells, not roads"""
        color = color_at(p)
        return color == bg

    # --- copy grid we will modify -------------------------------------------
    result: Grid = grid.copy()

    # Detect houses and roads
    houses, roads, road_points = detect_houses_and_roads(grid)

    # Find target houses (rarest color)
    a, b = find_target_houses(houses)

    # Get background color
    bg = grid.background_color

    # Find target house IDs using already detected houses
    house1_id = house2_id = None
    for i, house in enumerate(houses):
        if house.region == a.region:
            house1_id = i
        elif house.region == b.region:
            house2_id = i

    # Get expected path sequence
    unique_sequence = []
    if house1_id is not None and house2_id is not None:
        unique_sequence = construct_expected_path(house1_id, house2_id, roads, houses)
    
  
    # path replace color if Road to Gray and house to green
    for item in unique_sequence[1:-1]:
        if item.startswith('H'):
            house_idx = int(item[1:])
            if house_idx < len(houses):
                house = houses[house_idx]
                for point in house.points:
                    result[point.y][point.x] = Color.GREEN.value
        elif item.startswith('R'):
            road_idx = int(item[1:])
            if road_idx < len(roads):
                road = roads[road_idx]
                for point in road.points:
                    result[point.y][point.x] = Color.GRAY.value

    return result



if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]

    # Run the original route finder for comparison
    os.system("python main.py 7b0280bc route_finder")    