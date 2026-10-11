"""TaskPilot web interface API using only Python's standard library.
Run: python web_app.py, then open http://127.0.0.1:8000
"""
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from app import TaskManager

ROOT = Path(__file__).resolve().parent
manager = TaskManager()

class TaskPilotHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT / "web"), **kwargs)

    def send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def read_json(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            return json.loads(self.rfile.read(length).decode("utf-8")) if length else {}
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
            raise ValueError("Please send valid JSON.")

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/tasks":
            return self.send_json(manager.list_tasks())
        if path == "/api/summary":
            tasks = manager.list_tasks()
            summary = manager.summary()
            summary["high_priority"] = sum(1 for t in tasks if t["priority"] == "high" and not t["completed"])
            return self.send_json(summary)
        if path == "/":
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self):
        if urlparse(self.path).path != "/api/tasks":
            return self.send_json({"error": "Endpoint not found."}, 404)
        try:
            data = self.read_json()
            task = manager.add_task(data.get("title", ""), data.get("priority", "medium"))
            return self.send_json(task, 201)
        except ValueError as exc:
            return self.send_json({"error": str(exc)}, 400)

    def do_PATCH(self):
        parts = urlparse(self.path).path.strip("/").split("/")
        if len(parts) != 3 or parts[:2] != ["api", "tasks"]:
            return self.send_json({"error": "Endpoint not found."}, 404)
        try:
            task_id = int(parts[2])
            data = self.read_json()
            task = next((t for t in manager.list_tasks() if t["id"] == task_id), None)
            if task is None:
                raise KeyError(f"No task exists with ID {task_id}.")
            if "completed" in data:
                if data["completed"]:
                    manager.complete_task(task_id)
                else:
                    for stored in manager.tasks:
                        if stored["id"] == task_id:
                            stored["completed"] = False
                            manager.save()
                            break
            updated = next(t for t in manager.list_tasks() if t["id"] == task_id)
            return self.send_json(updated)
        except (ValueError, KeyError) as exc:
            return self.send_json({"error": str(exc)}, 400 if isinstance(exc, ValueError) else 404)

    def do_DELETE(self):
        parts = urlparse(self.path).path.strip("/").split("/")
        if len(parts) != 3 or parts[:2] != ["api", "tasks"]:
            return self.send_json({"error": "Endpoint not found."}, 404)
        try:
            task_id = int(parts[2])
            deleted = manager.delete_task(task_id)
            return self.send_json({"deleted": True, "task": deleted})
        except (ValueError, KeyError) as exc:
            return self.send_json({"error": str(exc)}, 404)

    def log_message(self, format, *args):
        # Keep the terminal output readable while still logging HTTP activity.
        print("[TaskPilot] " + (format % args))

if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8000), TaskPilotHandler)
    print("\nTaskPilot is running at http://127.0.0.1:8000")
    print("Keep this terminal open. Press Ctrl+C to stop the server.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nTaskPilot server stopped.")
    finally:
        server.server_close()
