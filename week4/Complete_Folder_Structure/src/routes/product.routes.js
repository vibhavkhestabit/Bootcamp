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

router.post("/", validate(createProductSchema), createProduct);

router.get("/", validate(listProductSchema, "query"), getProducts);

router.patch("/:id", validate(updateProductSchema), updateProduct);

router.delete("/:id", deleteProduct);

export default router;
