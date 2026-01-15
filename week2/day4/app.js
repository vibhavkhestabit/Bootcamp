import { saveTodos, loadTodos } from "./storage.js";

const form = document.getElementById("todo-form");
const input = document.getElementById("todo-input");
const list = document.getElementById("todo-list");

let todos = [];

// Debounce
function debounce(fn, delay = 300) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

// Throttle
function throttle(fn, limit = 500) {
  let inThrottle = false;
  return (...args) => {
    if (!inThrottle) {
      fn(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
}

// groupBy
function groupBy(arr, key) {
  return arr.reduce((acc, item) => {
    const group = item[key];
    acc[group] = acc[group] || [];
    acc[group].push(item);
    return acc;
  }, {});
}

function logError(error) {
  console.error("Error:", error.message);
}


try {
  todos = loadTodos();
  renderTodos();
} catch (error) {
  logError(error);
}

const addTodo = debounce(() => {
  const text = input.value.trim();
  if (!text) return;

  todos.push({
    id: Date.now(),
    text,
    completed: false
  });

  saveTodos(todos);
  renderTodos();
  input.value = "";
}, 300);

form.addEventListener("submit", (e) => {
  e.preventDefault();
  addTodo();
});


function renderTodos() {
  list.innerHTML = "";

  // Example usage of groupBy (completed vs pending)
  const grouped = groupBy(todos, "completed");

  [...(grouped.false || []), ...(grouped.true || [])].forEach(todo => {
    const li = document.createElement("li");
    if (todo.completed) li.classList.add("completed");

    const span = document.createElement("span");
    span.textContent = todo.text;
    span.onclick = throttle(() => toggleTodo(todo.id), 300);

    const actions = document.createElement("div");
    actions.className = "actions";

    const editBtn = document.createElement("button");
    editBtn.textContent = "✏️";
    editBtn.onclick = () => editTodo(todo.id);

    const deleteBtn = document.createElement("button");
    deleteBtn.textContent = "❌";
    deleteBtn.onclick = () => deleteTodo(todo.id);

    actions.append(editBtn, deleteBtn);
    li.append(span, actions);
    list.appendChild(li);
  });
}


function toggleTodo(id) {
  todos = todos.map(todo =>
    todo.id === id ? { ...todo, completed: !todo.completed } : todo
  );
  saveTodos(todos);
  renderTodos();
}


function editTodo(id) {
  const todo = todos.find(t => t.id === id);
  const newText = prompt("Edit todo:", todo.text);

  if (!newText || !newText.trim()) return;

  todo.text = newText.trim();
  saveTodos(todos);
  renderTodos();
}


function deleteTodo(id) {
  todos = todos.filter(todo => todo.id !== id);
  saveTodos(todos);
  renderTodos();
}
function showError(message) {
  const box = document.getElementById("error-box");
  box.textContent = message;
  box.classList.remove("hidden");

  setTimeout(() => {
    box.classList.add("hidden");
  }, 4000);
}
