import mongoose from 'mongoose';
import UserRepository from './repositories/user.repository.js';
import ProductRepository from './repositories/product.repository.js';
import connectDB from './loaders/db.js'; 

const seedDatabase = async () => {
    try {
        await connectDB();
        console.log('Connected to MongoDB');

        await mongoose.connection.collection('users').deleteMany({});
        await mongoose.connection.collection('products').deleteMany({});
        console.log('Creating New Users');

        const user1 = await UserRepository.create({
            firstName: 'Vibhav',
            lastName: 'Khaneja',
            email: 'vibhav.khaneja@hestabit.com',
            password: 'VibhavKhaneja',
            status: 'active'
        });

        const user2 = await UserRepository.create({
            firstName: 'Samarth',
            lastName: 'Singh',
            email: 'Sam@gmail.com',
            password: 'SamS',
            status: 'inactive'
        });

        console.log(`Created 2 users: ${user1.email}, ${user2.email}`);
        console.log('Creating Products');

        await ProductRepository.create({
            name: 'Gaming Laptop',
            price: 1200,
            createdBy: user1._id
        });

        await ProductRepository.create({
            name: 'Wireless Mouse',
            price: 25,
            createdBy: user2._id
        });

        await ProductRepository.create({
            name: 'HD Monitor',
            price: 300,
            createdBy: user1._id
        });

        console.log('Created 3 products');
        process.exit(0);

    } catch (error) {
        console.error('Seeding failed:', error);
        process.exit(1);
    }
};

seedDatabase();