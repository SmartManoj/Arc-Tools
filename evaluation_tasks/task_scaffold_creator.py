import os
from pyperclip import paste
from pymsgbox import prompt
from arc_tools.plot import remove_pngs
remove_pngs()
task_id = paste()
assert len(task_id) == 8, "Task ID must be 8 characters long"
function_name = prompt("Enter the function name:").replace(" ", "_")
code_snippet = f"""import os
from collections import Counter
from arc_tools.grid import Color, Grid, SubGrid, detect_objects, GridRegion, GridPoint, place_object_on_new_grid
from arc_tools import logger
from arc_tools.plot import plot_grids

def {function_name}(grid: Grid):
    '''
    add the function description first.
    '''
    return grid

if __name__ == "__main__":
    os.environ['initial_file'] = os.path.splitext(os.path.basename(__file__))[0]
    os.system("python main.py {task_id} {function_name}") 
"""
# find previous before marker in evaluation_tasks/tasks.py
with open("evaluation_tasks/tasks.py", "r+") as f:
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

from pyautogui import hotkey
hotkey("ctrl", "w")
hotkey("ctrl", "w")
# open the file in vscode
os.system(f"code {f.name}")

cmd = f"git add . && git commit -m {last_task_id+1}"
os.system(cmd)