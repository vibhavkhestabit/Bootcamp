const STORAGE_KEY = "todos";

export function saveTodos(todos) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(todos));
  } catch (error) {
    throw new Error("LocalStorage save failed");
  }
}

export function loadTodos() {
  try {
    const data = localStorage.getItem(STORAGE_KEY);
    return data ? JSON.parse(data) : [];
  } catch (error) {
    throw new Error("LocalStorage parse failed");
  }
}

