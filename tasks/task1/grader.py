import sys
import os
import importlib.util

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
grader_path = os.path.join(root_dir, 'grader.py')

spec = importlib.util.spec_from_file_location('root_grader', grader_path)
root_grader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(root_grader)
Grader = root_grader.Grader

def grade(trajectory=None, history=None, summary=None, **kwargs):
    h = trajectory if trajectory is not None else history
    if h is None:
        h = []
    g = Grader()
    report = g.grade(task_id=1, history=h, summary=summary or {})
    return max(0.1, min(0.9, float(report.final_score)))

if __name__ == '__main__':
    print(0.5)
