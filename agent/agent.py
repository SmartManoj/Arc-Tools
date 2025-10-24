from openai import OpenAI
import os
client = OpenAI(
  base_url=os.getenv("LLM_BASE_URL"),
  api_key=os.getenv("LLM_API_KEY"),
)

def get_response(messages):
  completion = client.chat.completions.create(
    model=os.getenv("LLM_MODEL"),
    messages=messages,
    stream=True,
    seed=42,
    temperature=0,
  )
  output = ""
  for chunk in completion:
      if content:=chunk.choices[0].delta.content:
          output += content
          print(content, end="", flush=True)
  print()  # New line after response
  return output

# Chat-based mode
conversation_history = []

data = open('C:\\Users\\smart\\Desktop\\GD\\ARC-AGI-2\\data\\evaluation\\7b5033c1.json', 'r').read()
import json
data = json.loads(data)
input_1 = (data['train'][0]['input'])
output_1 = (data['train'][0]['output'])

# Initial system context
initial_message = f"""
class GridPoint:
    def __init__(self, x, y, value):
        self.x = x
        self.y = y
        self.value = value

class GridRegion:
    attr x1, y1, x2, y2

class Grid(SafeList):
    def __init__(self, grid: list[list[int]], background_color: int | None = None,...)

class SubGrid(Grid):
    def __init__(self, region: GridRegion, parent_grid: Grid, obj_color: int | None = None, points: list[GridPoint] | None = None):
        attr region, 
        points : list[GridPoint] -> list of points in the subgrid

Find the transformation rule for the following input and output.
Input: {input_1}
Output: {output_1}

Write a Python function using the following API:
- Grid class: Grid(2d_list) - create a grid from a 2D list
- grid.get(x, y) - get value at position (x, y)
- detect_objects(grid) - return list of SubGrids (detects connected components)
- SubGrid.points - list of GridPoint objects in order

CRITICAL RULES:
1. Do NOT hardcode dimensions or positions
2. ALWAYS return Grid object: Grid([[val1], [val2], ...])
3. Keep solution SIMPLE - prefer 2-3 lines
4. Look for spatial patterns (straighten, align) not just color counting
5. For shape transformations, use object.points directly
6. All points in the SubGrid may not have the same value.
7. Input and Output are Grid Objects (2D list)

Example pattern:
```python
def transform(grid: Grid) -> Grid:
    result = grid.copy()
    objects = detect_objects(grid)
    return result
```

"""

conversation_history.append({"role": "user", "content": initial_message})
print("Assistant: ", end="", flush=True)
assistant_response = get_response(conversation_history)
conversation_history.append({"role": "assistant", "content": assistant_response})

# Chat loop
while True:
    user_input = input("\nYou: ").strip()
    if user_input.lower() in ['exit', 'quit', 'bye']:
        print("Goodbye!")
        break
    if not user_input:
        continue
    
    conversation_history.append({"role": "user", "content": user_input})
    print("Assistant: ", end="", flush=True)
    assistant_response = get_response(conversation_history)
    conversation_history.append({"role": "assistant", "content": assistant_response})
