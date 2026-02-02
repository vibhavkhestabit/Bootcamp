import { Router } from "express";
import {
  createProduct,
  getProducts,
  updateProduct,
  deleteProduct,
} from "../controllers/product.controller.js";

import validate from "../middlewares/validate.js";
import {
  createProductSchema,
  listProductSchema,
  updateProductSchema,
} from "../validations/product.validation.js";

const router = Router();

// 🔹 POST /api/products - Create a product
router.post(
  "/",
  validate(createProductSchema),
  createProduct
);

// 🔹 GET /api/products - Get all with filters/pagination
router.get(
  "/",
  validate(listProductSchema, "query"),
  getProducts
);

// 🔹 PATCH /api/products/:id - Update specific product
router.patch(
  "/:id",
  validate(updateProductSchema),
  updateProduct
);

// 🔹 DELETE /api/products/:id - Soft delete product
router.delete("/:id", deleteProduct);

export default router;
