import dotenv from 'dotenv';
dotenv.config();

import app from './app.js';
import connectDB from './db.js';
import mainRouter from './server.js';

const PORT = process.env.PORT || 3000;

connectDB();

app.use('/api', mainRouter);

app.listen(PORT, () => {
    console.log(` Sneaker Backend running on port ${PORT}`);
});