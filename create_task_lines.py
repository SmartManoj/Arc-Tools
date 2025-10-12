import os

files = []
for f in sorted(os.listdir('evaluation_tasks')):
    if f.startswith('task_') and f.endswith('.py') and f not in ['task_scaffold_creator.py', 'tasks.py']:
        line_count = sum(1 for _ in open(os.path.join('evaluation_tasks', f)))
        files.append((f, line_count))

sorted_files = sorted(files, key=lambda x: x[1])

with open('task_lines.txt', 'w') as output:
    for name, lines in sorted_files:
        task_num = name.replace('task_', '').replace('.py', '')
        output.write(f'{task_num}: {lines}\n')

print(f"Created task_lines.txt with {len(sorted_files)} tasks")

