from arc_tools.grid import Grid, detect_objects, Color, SubGrid, GridRegion, GridPoint
from arc_tools.plot import plot_grid, plot_grids

def find_nearby_two_dots(sgrid: SubGrid, parent_grid: Grid) -> SubGrid:
    """
    find nearby two dots of different color.
    """
    # Get all non-background colors in the grid
    # expand the region by 2 * 2
    expanded_grid = sgrid.expand(2).get_full_grid()
    # fill background color on corners of the expanded grid
    expanded_grid = expanded_grid.clear_corners(grid_size=2, relative_to=sgrid)
    plot_grid(expanded_grid, show=0, save_all=True)
    objects = detect_objects(expanded_grid, ignore_color=Color.LIGHT_BLUE)
    plot_grids(objects, show=0, save_all=True)
    return [obj for obj in objects if obj.get_total_dots() == 2][0]
    


def dot_to_object(grid: Grid) -> Grid:
    """
    light blue box is the key object.
    nearby two objects of different color is the color replacement map.
    (need to replace the color with the one that touched the key object)
    extract all the information from the grid.
    replace dots with the object using the color replacement map (don't replace already replaced dots).
    remove the key object and the color replacement map from the grid.
    """
    objects = detect_objects(grid, required_color=Color.LIGHT_BLUE)
    for obj in objects[::-1]:
        if len(obj.get_unique_values()) != 1:
            # split the object vertically if height > width
            if obj.region.height > obj.region.width:
                # split the object vertically
                center_x = obj.region.width // 2 - 1
                center_y = obj.region.y2
                region1 = GridRegion([GridPoint(obj.region.x1, obj.region.y1), GridPoint(center_x, obj.region.y2)])
                region2 = GridRegion([GridPoint(center_x + 1, obj.region.y1), GridPoint(obj.region.x2, obj.region.y2)])
                obj1 = detect_objects(SubGrid(region1, grid).get_full_grid(), required_color=Color.LIGHT_BLUE)[0]
                obj1 = SubGrid(obj1.region, grid)
                obj2 = detect_objects(SubGrid(region2, grid).get_full_grid(), required_color=Color.LIGHT_BLUE)[0]
                obj2 = SubGrid(obj2.region, grid)
                objects.append(obj1)
                objects.append(obj2)
                objects.remove(obj)
            else:
                # split the object horizontally
                center_x = obj.region.x1
                center_y = obj.region.height // 2 - 1
                region1 = GridRegion([GridPoint(obj.region.x1, obj.region.y1), GridPoint(obj.region.x2, center_y)])
                region2 = GridRegion([GridPoint(obj.region.x1, center_y + 1), GridPoint(obj.region.x2, obj.region.y2)])
                obj1 = detect_objects(SubGrid(region1, grid).get_full_grid(), required_color=Color.LIGHT_BLUE)[0]
                obj1 = SubGrid(obj1.region, grid)
                obj2 = detect_objects(SubGrid(region2, grid).get_full_grid(), required_color=Color.LIGHT_BLUE)[0]
                obj2 = SubGrid(obj2.region, grid)
                objects.append(obj1)
                objects.append(obj2)
                objects.remove(obj)

    replacement_details = []
    for obj in objects[:]:
        color_replacement_map = find_nearby_two_dots(obj, grid)
        first_value = grid[color_replacement_map.region.y1][color_replacement_map.region.x1]
        second_value = grid[color_replacement_map.region.y2][color_replacement_map.region.x2]
        # plot_grids([filtered_object, parent_grid], show=1)
        background_color = grid.background_color
        grid[color_replacement_map.region.y1][color_replacement_map.region.x1] = background_color
        grid[color_replacement_map.region.y2][color_replacement_map.region.x2] = background_color
        if color_replacement_map.region.x2 + 1 == obj.region.x1 or color_replacement_map.region.y2 + 1 == obj.region.y1:
            dot_color, object_color = first_value, second_value
        else:
            dot_color, object_color = second_value, first_value
        obj = obj.replace_color(Color.LIGHT_BLUE.value, object_color)
        dx, dy = obj.region.x1 - color_replacement_map.region.x1  , obj.region.y1 - color_replacement_map.region.y1
        # move one step forward towards the object
        # if obj is above, move up
        if obj.region.y2 < color_replacement_map.region.y1:
            dy += 1
        # if obj is below, move down
        elif obj.region.y1 > color_replacement_map.region.y2:
            dy -= 2
        # if obj is left, move left
        elif obj.region.x2 < color_replacement_map.region.x1:
            dx += 1
        # if obj is right, move right
        else:
            dx -= 2
        replacement_details.append((dot_color, obj, dx, dy))
        grid = grid.remove_object(obj)
        plot_grid(grid, show=0, save_all=True)
    first_grid = grid.copy()
    for dot_color, obj, dx, dy in replacement_details:
        grid = grid.replace_dot(dot_color, obj, dx, dy, first_grid)
        plot_grids([grid, first_grid], show=0, save_all=True)
    # plot_grid(grid, show=0, save_all=True)
    return grid


if __name__ == "__main__":
    import os
    os.system("main.py abc82100 dot_to_object")
