const listEl = document.getElementById('todo-list');
const inputEl = document.getElementById('todo-text');
const addBtn = document.getElementById('add-btn');
const countEl = document.getElementById('count');

async function fetchTodos() {
  const res = await fetch('/api/todos');
  if (!res.ok) throw new Error('Failed to fetch todos');
  return res.json();
}

async function addTodo(text) {
  const res = await fetch('/api/todos', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    alert(err.error || 'Failed to add');
    return null;
  }
  return res.json();
}

async function toggleTodo(id, done) {
  const res = await fetch(`/api/todos/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ done })
  });
  return res.ok;
}

async function deleteTodo(id) {
  const res = await fetch(`/api/todos/${id}`, { method: 'DELETE' });
  return res.ok;
}

function renderItem(todo) {
  const li = document.createElement('li');
  li.className = 'todo';

  const cb = document.createElement('input');
  cb.type = 'checkbox';
  cb.checked = !!todo.done;
  cb.addEventListener('change', async () => {
    const ok = await toggleTodo(todo.id, cb.checked);
    if (ok) {
      textEl.classList.toggle('done', cb.checked);
      updateCount();
    }
  });

  const textEl = document.createElement('span');
  textEl.className = 'text' + (todo.done ? ' done' : '');
  textEl.textContent = todo.text;

  const actions = document.createElement('div');
  actions.className = 'actions';

  const delBtn = document.createElement('button');
  delBtn.textContent = 'Delete';
  delBtn.addEventListener('click', async () => {
    const ok = await deleteTodo(todo.id);
    if (ok) {
      li.remove();
      updateCount();
    }
  });

  actions.appendChild(delBtn);
  li.appendChild(cb);
  li.appendChild(textEl);
  li.appendChild(actions);
  return li;
}

function updateCount() {
  const total = listEl.children.length;
  const done = Array.from(listEl.children).filter(li => li.querySelector('input[type="checkbox"]').checked).length;
  countEl.textContent = `${done}/${total} completed`;
}

async function refresh() {
  listEl.innerHTML = '';
  const items = await fetchTodos();
  items.forEach(t => listEl.appendChild(renderItem(t)));
  updateCount();
}

addBtn.addEventListener('click', async () => {
  const text = inputEl.value.trim();
  if (!text) return;
  const created = await addTodo(text);
  if (created) {
    listEl.appendChild(renderItem(created));
    inputEl.value = '';
    updateCount();
  }
});

inputEl.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') addBtn.click();
});

refresh();
