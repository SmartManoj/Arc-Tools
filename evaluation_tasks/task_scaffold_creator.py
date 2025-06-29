from pyperclip import paste
task_id = paste()
function_name = "build_a_box"
code_snippet = f"""import os
from collections import Counter
from arc_tools.grid import Color, Grid, SubGrid, detect_objects, GridRegion, GridPoint, place_object_on_new_grid

def {function_name}(grid: Grid):
    '''
    
    '''
    return grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py {task_id} {function_name}") 
"""
# find previous before marker in C:\Users\smart\Desktop\GD\ARC Tools\evaluation_tasks\tasks.py
with open("C:\\Users\\smart\\Desktop\\GD\\ARC Tools\\evaluation_tasks\\tasks.py", "r+") as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if "marker" in line:
            break
    last_task_id = int(lines[i-1].split("from task_")[1].split(" ")[0])
    lines.insert(i, f"from task_{last_task_id+1} import {function_name}\n")
    f.seek(0)
    f.writelines(lines)

with open(f"evaluation_tasks/task_{last_task_id+1}.py", "w") as f: 
    f.write(code_snippet)





