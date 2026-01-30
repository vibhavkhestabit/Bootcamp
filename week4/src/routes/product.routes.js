import { Router } from "express";
import { 
  createProduct, 
  getProducts, 
  updateProduct, 
  deleteProduct 
} from "../controllers/product.controller.js";

const router = Router();

// 🔹 POST /api/products - Create a product
router.post("/", createProduct);

// 🔹 GET /api/products - Get all with filters/pagination
router.get("/", getProducts);

// 🔹 PATCH /api/products/:id - Update specific product
router.patch("/:id", updateProduct);

// 🔹 DELETE /api/products/:id - Soft delete product
router.delete("/:id", deleteProduct);

export default router;