import express from 'express';
import os from 'os';

const app = express();
const port = 3000;

app.get('/', (req, res) => {
    // Gets the Container ID (e.g., "8a7b9c...")
    const containerID = os.hostname();
    
    console.log(`Request served by container: ${containerID}`);
    
    res.send(`
        <div style="font-family: sans-serif; text-align: center; padding: 50px;">
            <h1>Load Balancing Demo</h1>
            <p>Response served by Container ID:</p>
            <h2 style="color: blue; border: 2px solid blue; display: inline-block; padding: 10px;">${containerID}</h2>
        </div>
    `);
});

app.listen(port, () => {
    console.log(`Backend server started on port ${port}`);
});