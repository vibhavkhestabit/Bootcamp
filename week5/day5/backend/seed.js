import dotenv from 'dotenv';
dotenv.config();

import mongoose from 'mongoose';
import Product from './product.model.js';

const MONGO_URI = process.env.MONGO_URL || 'mongodb://mongo:27017/sneaker-hub';

const initialProducts = [
    {
        name: "Puma RS-X",
        brand: "Puma",
        price: 8999,
        size: 9,
        image: "https://images.unsplash.com/photo-1608231387042-66d1773070a5?auto=format&fit=crop&w=500&q=80",
        condition: "New",
        rating: 4.6, 
        description: "Chunky design with street influence."
    },
    {
        name: "Air Jordan 1",
        brand: "Nike",
        price: 13999,
        size: 10,
        image: "https://images.unsplash.com/photo-1552346154-21d32810aba3?auto=format&fit=crop&w=500&q=80",
        condition: "New",
        rating: 4.9, 
        description: "Iconic silhouette loved worldwide."
    },
    {
        name: "Vans Old Skool",
        brand: "Vans",
        price: 4999,
        size: 8,
        image: "https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?auto=format&fit=crop&w=500&q=80",
        condition: "New",
        rating: 4.2, 
        description: "Skate style with everyday comfort."
    },
    {
        name: "Nike Air Max",
        brand: "Nike",
        price: 11999,
        size: 9,
        image: "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=500&q=80",
        condition: "New",
        rating: 4.7,
        description: "Everyday comfort with timeless design."
    },
    {
        name: "Adidas Forum",
        brand: "Adidas",
        price: 9999,
        size: 9,
        image: "https://images.unsplash.com/photo-1587563871167-1ee9c731aefb?auto=format&fit=crop&w=500&q=80",
        condition: "New",
        rating: 4.0,
        description: "Classic basketball-inspired silhouette."
    },
    {
        name: "NB 574",
        brand: "New Balance",
        price: 8499,
        size: 9,
        image: "https://images.unsplash.com/photo-1551107696-a4b0c5a0d9a2?auto=format&fit=crop&w=500&q=80",
        condition: "New",
        rating: 4.6,
        description: "Retro style meets modern comfort."
    },
    {
        name: "Converse Chuck",
        brand: "Converse",
        price: 3999,
        size: 8,
        image: "https://images.unsplash.com/photo-1607522370275-f14206c193a7?auto=format&fit=crop&w=500&q=80",
        condition: "New",
        rating: 4.8,
        description: "Bold design with street appeal."
    },
    {
        name: "Yeezy Boost",
        brand: "Adidas",
        price: 24999,
        size: 10,
        image: "https://images.unsplash.com/photo-1588117260148-447884962ca5?auto=format&fit=crop&w=500&q=80",
        condition: "New",
        rating: 5.0,
        description: "Ultimate comfort and hype."
    }
];

const seedDB = async () => {
    try {
        await mongoose.connect(MONGO_URI);
        console.log(" Connected to DB for Seeding...");
        
        await Product.deleteMany({});
        await Product.insertMany(initialProducts);
        
        console.log(" Database seeded with WEB IMAGES!");
        process.exit();
    } catch (err) {
        console.error(err);
        process.exit(1);
    }
};

seedDB();