# @test-project

A minimal full‑stack app with a Python (Flask) backend and a static HTML/CSS/JS frontend.

The backend also serves the frontend, so you can run everything with one command.

## Structure

- `backend/` — Flask app and Python deps
- `frontend/` — `index.html`, `styles.css`, `app.js`

## Run (Windows PowerShell)

1. Create a virtual environment (optional but recommended):
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
2. Install dependencies:
   ```powershell
   pip install -r backend\requirements.txt
   ```
3. Start the server:
   ```powershell
   python backend\app.py
   ```
4. Open the app:
   - Navigate to http://127.0.0.1:5000/

## API

- `GET /api/todos` → list todos
- `POST /api/todos` body `{ text: string }` → create
- `PATCH /api/todos/{id}` body `{ text?: string, done?: boolean }` → update
- `DELETE /api/todos/{id}` → remove

Data is stored in memory and resets on server restart.
