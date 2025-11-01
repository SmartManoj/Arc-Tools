from arc_tools.grid import Grid, detect_objects, move_object
from arc_tools.logger import logger
import json
def solve_task(task_fn):
    with open('data.json', 'r') as file:
        data = json.load(file)
    train_data = data['train']
    test_data = data['test']
    is_passed = False
    for task_idx, task in enumerate(train_data, 1):
        output = task_fn(Grid(task['input']))
        if not output.compare(task['output']):
            print(f"Train Task {task_idx} failed")
            break
        logger.info(f"Train Task {task_idx} passed")
    else:
        is_passed = True
    if is_passed:
        outputs = []
        for task_idx, task in enumerate(test_data, 1):
            output = task_fn(Grid(task['input']))
            outputs.append({"attempt_1": output, "attempt_2": output})
            logger.info(f"Test Task {task_idx} output successfully generated")
        with open('output.json', 'w') as file:
            json.dump(outputs, file)
    