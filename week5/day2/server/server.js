const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');

const app = express();
app.use(cors());

const MONGO_URI = process.env.MONGO_URI || 'mongodb://mongo:27017/testdb';

const connectWithRetry = () => {
  console.log('Attempting MongoDB connection...');
  
  mongoose.connect(MONGO_URI)
    .then(() => {
      console.log('MongoDB Connected successfully!');
    })
    .catch(err => {
      console.log('MongoDB connection failed. Waiting 5 seconds to retry...');
      setTimeout(connectWithRetry, 5000);
    });
};

connectWithRetry();

app.get('/', (req, res) => {
  res.send('Message from server and task completion');
});

app.listen(5000, () => {
  console.log('Server running on port 5000');
});