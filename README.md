# TaskPilot — AI-Assisted Task Manager

A small Python task manager with a polished browser dashboard. Tasks are saved locally in `tasks.json`; the web server and UI use only the Python standard library (the page optionally loads the DM Sans font from Google Fonts when internet is available).

## Web version (recommended)
1. Open this `TaskPilot` folder in VS Code.
2. In the terminal, run `python web_app.py`.
3. Open **http://127.0.0.1:8000** in your browser.
4. Keep the terminal open while using the site. Press `Ctrl+C` in the terminal to stop it.

The website supports adding tasks, priority selection, searching, filtering, marking tasks complete/in progress, deleting tasks, and live summary cards. Data is saved to the same `tasks.json` file used by the command-line version. The server binds to `127.0.0.1`, so it is for use on your own computer, not public hosting.

## Command-line version
Run `python app.py`.

## Automated tests
Run `python -m unittest -v`. Tests use temporary files and do not alter your real `tasks.json`.

## Notes for the assignment
Keep a record of prompts actually used, code changes accepted/rejected, terminal output, and screenshots. Do not claim results until you have run the tests yourself. If you include the website in your report, explain that the browser frontend sends requests to a Python HTTP server, which uses the existing `TaskManager` class and JSON file for persistence.
