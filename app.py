"""
TaskPilot: a small task manager built with AI-assisted development.
Storage: local JSON file in the same directory as this script.
Run: python app.py
Tests: python -m unittest -v
"""
import json
from pathlib import Path

DEFAULT_FILE = Path(__file__).with_name("tasks.json")
VALID_PRIORITIES = {"low", "medium", "high"}


class TaskManager:
    def __init__(self, storage_path=DEFAULT_FILE):
        self.storage_path = Path(storage_path)
        self.tasks = []
        self.load()

    def load(self):
        """Load saved tasks. A missing file means a new, empty task list."""
        if not self.storage_path.exists():
            self.tasks = []
            return
        try:
            with self.storage_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
            if not isinstance(data, list):
                raise ValueError("Task data must be a JSON list.")
            # Validate each record rather than silently accepting malformed data.
            for item in data:
                if not isinstance(item, dict):
                    raise ValueError("Each task must be a JSON object.")
                if not {"id", "title", "priority", "completed"} <= item.keys():
                    raise ValueError("A task is missing required fields.")
            self.tasks = data
        except (json.JSONDecodeError, ValueError) as exc:
            raise ValueError(f"Could not load task file: {exc}") from exc

    def save(self):
        """Write the current task list to disk."""
        with self.storage_path.open("w", encoding="utf-8") as file:
            json.dump(self.tasks, file, indent=2, ensure_ascii=False)

    def add_task(self, title, priority="medium"):
        title = title.strip() if isinstance(title, str) else ""
        priority = priority.lower() if isinstance(priority, str) else ""
        if not title:
            raise ValueError("Task title cannot be empty.")
        if priority not in VALID_PRIORITIES:
            raise ValueError("Priority must be low, medium, or high.")
        next_id = max((task["id"] for task in self.tasks), default=0) + 1
        task = {
            "id": next_id,
            "title": title,
            "priority": priority,
            "completed": False,
        }
        self.tasks.append(task)
        self.save()
        return task.copy()

    def list_tasks(self):
        return [task.copy() for task in self.tasks]

    def complete_task(self, task_id):
        task = self._find_task(task_id)
        task["completed"] = True
        self.save()
        return task.copy()

    def delete_task(self, task_id):
        task = self._find_task(task_id)
        self.tasks.remove(task)
        self.save()
        return task.copy()

    def _find_task(self, task_id):
        for task in self.tasks:
            if task["id"] == task_id:
                return task
        raise KeyError(f"No task exists with ID {task_id}.")

    def summary(self):
        total = len(self.tasks)
        completed = sum(1 for task in self.tasks if task["completed"])
        return {"total": total, "completed": completed, "pending": total - completed}


def display_tasks(manager):
    tasks = manager.list_tasks()
    if not tasks:
        print("\nNo tasks yet.")
        return
    print("\nID | Status | Priority | Task")
    print("-" * 48)
    for task in tasks:
        status = "Done" if task["completed"] else "Pending"
        print(f'{task["id"]:>2} | {status:<7} | {task["priority"]:<8} | {task["title"]}')


def main():
    manager = TaskManager()
    while True:
        print("\n=== TaskPilot ===")
        print("1. Add task")
        print("2. View tasks")
        print("3. Mark task complete")
        print("4. Delete task")
        print("5. Summary")
        print("0. Exit")
        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                title = input("Task title: ")
                priority = input("Priority (low/medium/high, default medium): ").strip().lower() or "medium"
                task = manager.add_task(title, priority)
                print(f'Added task #{task["id"]}: {task["title"]}')
            elif choice == "2":
                display_tasks(manager)
            elif choice == "3":
                task_id = int(input("Task ID to complete: "))
                task = manager.complete_task(task_id)
                print(f'Marked "{task["title"]}" as complete.')
            elif choice == "4":
                task_id = int(input("Task ID to delete: "))
                task = manager.delete_task(task_id)
                print(f'Deleted "{task["title"]}".')
            elif choice == "5":
                stats = manager.summary()
                print(f'Total: {stats["total"]} | Completed: {stats["completed"]} | Pending: {stats["pending"]}')
            elif choice == "0":
                print("Goodbye!")
                break
            else:
                print("Invalid option. Please choose 0–5.")
        except ValueError as exc:
            print(f"Input error: {exc}")
        except KeyError as exc:
            print(f"Task error: {exc}")


if __name__ == "__main__":
    main()
