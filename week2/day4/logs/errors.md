# Error Logs – Todo App

## LocalStorage Parse Error
- Triggered when corrupted JSON exists in LocalStorage
- Handled using try/catch in storage.js

This error occurs when our local storage is unable to be fetched and stored.
We have created the path in the file storage.js where we Parse our data from their and import it in App.js

export function loadTodos() {
  try {
    const data = localStorage.getItem(STORAGE_KEY);
    return data ? JSON.parse(data) : [];
  } catch (error) {
    throw new Error("LocalStorage parse failed");
  }
}

If theres any missing items or issues in this piece of logic, then our function of loadTodos wont work and we will face a LocalStorage parse failed error.

![Screenshot of Parse UI](screenshots/parseUI.png)
![Screenshot of Parse UI](screenshots/parse.png)

## LocalStorage Load Error

This error takes place while adding data to local storage using storage.js file
export function saveTodos(todos) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(todos));
  } catch (error) {
    throw new Error("LocalStorage save failed");
  }
}

So if theres any error, anything missing while creating the path to either fetching it in Storage.js or any issues for handling todos get it will give a LocalStorage save failed error

![Screenshot of Parse UI](screenshots/load.png)




