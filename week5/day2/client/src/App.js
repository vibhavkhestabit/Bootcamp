import React, { useEffect, useState } from 'react';
import './App.css'; // <--- THIS WAS MISSING!

function App() {
  const [message, setMessage] = useState('Loading...');

  useEffect(() => {
    fetch('http://localhost:5000/')
      .then(res => res.text())
      .then(data => setMessage(data))
      .catch(err => setMessage('Error connecting to server'));
  }, []);

  return (
    <div className="App">
      <h1>Completion of Day 2 Task of Connectivity Successful: {message}</h1>
    </div>
  );
}

export default App;