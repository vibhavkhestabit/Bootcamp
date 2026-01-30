import { Router } from "express";
import productRoutes from "./product.routes.js";

const router = Router();

// 🔹 Health Check
router.get("/health", (req, res) => {
  res.status(200).send("healthy");
});

// 🔹 Mount Feature Routes
// This means all routes in productRoutes will start with /products
router.use("/products", productRoutes);

// 🔹 404 handler (always last)
router.use((req, res) => {
  res.status(404).json({ 
    success: false,
    message: `Cannot find ${req.originalUrl} on this server`,
    code: "ROUTE_NOT_FOUND"
  });
});

export default router;