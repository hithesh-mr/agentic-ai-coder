from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='../frontend', static_url_path='', template_folder='../frontend')

# In-memory todo store
todos = []
next_id = 1

@app.get('/api/todos')
def list_todos():
    return jsonify(todos)

@app.post('/api/todos')
def add_todo():
    global next_id
    data = request.get_json(force=True, silent=True) or {}
    text = (data.get('text') or '').strip()
    if not text:
        return jsonify({'error': 'text is required'}), 400
    todo = {'id': next_id, 'text': text, 'done': False}
    next_id += 1
    todos.append(todo)
    return jsonify(todo), 201

@app.patch('/api/todos/<int:todo_id>')
def update_todo(todo_id):
    data = request.get_json(force=True, silent=True) or {}
    for todo in todos:
        if todo['id'] == todo_id:
            if 'text' in data:
                text = (data['text'] or '').strip()
                if not text:
                    return jsonify({'error': 'text cannot be empty'}), 400
                todo['text'] = text
            if 'done' in data:
                todo['done'] = bool(data['done'])
            return jsonify(todo)
    return jsonify({'error': 'not found'}), 404

@app.delete('/api/todos/<int:todo_id>')
def delete_todo(todo_id):
    global todos
    before = len(todos)
    todos = [t for t in todos if t['id'] != todo_id]
    if len(todos) == before:
        return jsonify({'error': 'not found'}), 404
    return '', 204

# Serve frontend
@app.get('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True)
