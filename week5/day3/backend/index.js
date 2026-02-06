import express from 'express';
import os from 'os';

const app = express();
const port = 3000;

app.get('/api', (req, res) => {
    const containerID = os.hostname();
    
    console.log(`Request served by container: ${containerID}`);
    
    res.send(`
        <div style="font-family: sans-serif; text-align: center; padding: 50px;">
            <h1>Day 3 Task Completion</h1>
            <p>Week 5 Day 3, Using Ngnix Load Balancer to replicate instances and this is our container id:</p>
            <h2 style="color: blue; border: 2px solid blue; display: inline-block; padding: 10px;">${containerID}</h2>
        </div>
    `);
});

app.listen(port, () => {
    console.log(`Backend server started on port ${port}`);
});