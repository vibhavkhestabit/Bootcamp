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

// POST /api/products
router.post("/", validate(createProductSchema), createProduct);

// GET /api/products
router.get("/", validate(listProductSchema, "query"), getProducts);

// PATCH /api/products/:id
router.patch("/:id", validate(updateProductSchema), updateProduct);

// DELETE /api/products/:id
router.delete("/:id", deleteProduct);

export default router;
