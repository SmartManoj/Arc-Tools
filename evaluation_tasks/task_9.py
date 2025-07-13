from arc_tools.grid import Grid, Color

plus_pos = (-1,1),(0,1),(1,1),(0,2)

def is_plus(x,y,grid):
    for dx,dy in plus_pos:
        if grid[y+dy][x+dx] != Color.YELLOW.value:
            return False
    return True

def highlight_plus(grid: Grid) -> Grid:
    '''
    replace yellow plus with light blue plus
    '''
    for y in range(grid.height):
        for x in range(grid.width):
            if grid[y][x] == Color.YELLOW.value:
                if is_plus(x,y,grid):
                    grid[y][x] = Color.LIGHTBLUE.value
                    for dx,dy in plus_pos:
                        grid[y+dy][x+dx] = Color.LIGHTBLUE.value
    return grid

if __name__ == "__main__":
    import os
    os.system("python main.py 1818057f highlight_plus")