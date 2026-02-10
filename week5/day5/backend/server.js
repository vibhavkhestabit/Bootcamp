import express from 'express';
import Product from './product.model.js'; 

const router = express.Router();

router.get('/products', async (req, res) => {
    try {
        let sortQuery = { createdAt: -1 }; 

        if (req.query.sort === 'rating_desc') {
            sortQuery = { rating: -1 };
        } else if (req.query.sort === 'price_asc') {
            sortQuery = { price: 1 };
        } else if (req.query.sort === 'price_desc') {
            sortQuery = { price: -1 };
        }

        const products = await Product.find({ isDeleted: { $ne: true } }).sort(sortQuery);
        res.status(200).json(products);
    } catch (err) {
        res.status(500).json({ error: 'Failed to fetch products' });
    }
});

router.get('/products/:id', async (req, res) => {
    try {
        const product = await Product.findById(req.params.id);
        if (!product) return res.status(404).json({ error: 'Product not found' });
        res.status(200).json(product);
    } catch (err) {
        res.status(500).json({ error: 'Server Error' });
    }
});

router.post('/products', async (req, res) => {
    try {
        const newProduct = new Product(req.body);
        const savedProduct = await newProduct.save();
        res.status(201).json(savedProduct);
    } catch (err) {
        res.status(400).json({ error: err.message });
    }
});

router.patch('/products/:id', async (req, res) => {
    try {
        const updatedProduct = await Product.findByIdAndUpdate(
            req.params.id, 
            req.body, 
            { new: true, runValidators: true } 
        );
        if (!updatedProduct) return res.status(404).json({ error: 'Product not found' });
        res.status(200).json(updatedProduct);
    } catch (err) {
        res.status(400).json({ error: err.message });
    }
});

router.delete('/products/:id', async (req, res) => {
    try {
        const softDeletedProduct = await Product.findByIdAndUpdate(
            req.params.id,
            { isDeleted: true },
            { new: true }
        );

        if (!softDeletedProduct) return res.status(404).json({ error: 'Product not found' });
        res.status(200).json({ message: 'Product moved to trash (Soft Deleted)' });
    } catch (err) {
        res.status(500).json({ error: 'Server Error' });
    }
});

export default router;