import { Router } from "express";
import productRoutes from "./product.routes.js";

const router = Router();

router.get("/health", (req, res) => {
  res.status(200).send("healthy");
});

router.use("/products", productRoutes);

router.use((req, res) => {
  res.status(404).json({ 
    success: false,
    message: `Cannot find ${req.originalUrl} on this server`,
    code: "ROUTE_NOT_FOUND"
  });
});

export default router;