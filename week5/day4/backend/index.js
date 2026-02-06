import express from 'express';
import os from 'os';

const app = express();
const PORT = 3000;

// Get the Container ID (Hostname) to prove Load Balancing works
const containerID = os.hostname();

app.get('/', (req, res) => {
    console.log(`Request handled by: ${containerID}`);
    res.send(`
        <div style="font-family: sans-serif; text-align: center; padding: 50px;">
            <h1>Secure HTTPS Backend</h1>
            <p>Served by Container ID:</p>
            <h2 style="color: blue;">${containerID}</h2>
        </div>
    `);
});

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT} inside container ${containerID}`);
});