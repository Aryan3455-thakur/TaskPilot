import json
import tempfile
import unittest
from pathlib import Path

from app import TaskManager


class TestTaskManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = Path(self.temp_dir.name) / "tasks.json"
        self.manager = TaskManager(self.file_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_new_manager_starts_empty(self):
        self.assertEqual(self.manager.list_tasks(), [])

    def test_add_task_trims_title_and_defaults(self):
        task = self.manager.add_task("  Finish report  ")
        self.assertEqual(task["title"], "Finish report")
        self.assertEqual(task["priority"], "medium")
        self.assertFalse(task["completed"])

    def test_rejects_empty_title(self):
        with self.assertRaises(ValueError):
            self.manager.add_task("   ")

    def test_rejects_invalid_priority(self):
        with self.assertRaises(ValueError):
            self.manager.add_task("Study", "urgent")

    def test_completes_task(self):
        task = self.manager.add_task("Study Python")
        updated = self.manager.complete_task(task["id"])
        self.assertTrue(updated["completed"])

    def test_deletes_task(self):
        task = self.manager.add_task("Submit assignment")
        self.manager.delete_task(task["id"])
        self.assertEqual(self.manager.list_tasks(), [])

    def test_unknown_id_raises_key_error(self):
        with self.assertRaises(KeyError):
            self.manager.complete_task(999)

    def test_tasks_persist_after_reload(self):
        self.manager.add_task("Persist me", "high")
        second_manager = TaskManager(self.file_path)
        self.assertEqual(second_manager.list_tasks()[0]["title"], "Persist me")
        self.assertEqual(second_manager.list_tasks()[0]["priority"], "high")

    def test_summary_counts(self):
        first = self.manager.add_task("One")
        self.manager.add_task("Two")
        self.manager.complete_task(first["id"])
        self.assertEqual(
            self.manager.summary(),
            {"total": 2, "completed": 1, "pending": 1},
        )

    def test_corrupt_json_is_reported(self):
        self.file_path.write_text("{not valid json", encoding="utf-8")
        with self.assertRaises(ValueError):
            TaskManager(self.file_path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
