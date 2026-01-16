const STORAGE_KEY = "todos";

export function saveTodos(todos) {
  try {
    localStorage.setItem( STORAGE_KEY, JSON.stringify(todos));
    if(STORAGE_KEY !== "todos"){
    throw new Error("LocalStorage save failed");
    }
  } catch (error) {
    console.error("Save Failed",error)
  }
}

export function loadTodos() {
  try {
    const data = localStorage.getItem(STORAGE_KEY);
    return data ? JSON.parse(data) : [];
  } catch (error) {
    console.error("Load Failed",error)
  }
}

