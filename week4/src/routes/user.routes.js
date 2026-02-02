import { Router } from "express";
import {
  createUser,
  getUsers,
  updateUser,
  deleteUser,
} from "../controllers/user.controller.js";

import validate from "../middlewares/validate.js";
import {
  createUserSchema,
  listUserSchema,
  updateUserSchema,
} from "../validations/user.validation.js";

const router = Router();

// 🔹 POST /api/users - Create a user
router.post(
  "/",
  validate(createUserSchema),
  createUser
);

// 🔹 GET /api/users - Get users (paginated)
router.get(
  "/",
  validate(listUserSchema, "query"),
  getUsers
);

// 🔹 PATCH /api/users/:id - Update user
router.patch(
  "/:id",
  validate(updateUserSchema),
  updateUser
);

// 🔹 DELETE /api/users/:id - Delete user
router.delete("/:id", deleteUser);

export default router;
