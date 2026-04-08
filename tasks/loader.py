import json
import os
import importlib.util

TASKS_DIR = "tasks"

def load_tasks():
    loaded = []

    for folder in os.listdir(TASKS_DIR):
        path = os.path.join(TASKS_DIR, folder)

        if not os.path.isdir(path):
            continue

        task_file = os.path.join(path, "task.json")
        grader_file = os.path.join(path, "grader.py")

        if not os.path.exists(task_file) or not os.path.exists(grader_file):
            continue

        with open(task_file, "r", encoding="utf-8") as f:
            task = json.load(f)

        spec = importlib.util.spec_from_file_location(f"{folder}_grader", grader_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        loaded.append({
            "task": task,
            "grader": module.grade,
        })

    return loaded