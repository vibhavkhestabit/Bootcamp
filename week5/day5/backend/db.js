import mongoose from 'mongoose';

const MONGO_URI = process.env.MONGO_URL || 'mongodb://mongo:27017/sneaker-hub';

const connectDB = async () => {
    try {
        await mongoose.connect(MONGO_URI);
        console.log(' MongoDB Connected Successfully');
    } catch (err) {
        console.error(' MongoDB Connection Error:', err.message);
    }
};

export default connectDB;