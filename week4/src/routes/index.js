import { Router } from "express";

const router = Router();

router.get("/", (req, res) => {
  res.status(200).json({ message: "OK" });
});

router.get("/health", (req, res) => {
  res.status(200).json({ status: "healthy" });
});

// 404 handler (always last)
router.use((req, res) => {
  res.status(404).json({ message: "Not Found" });
});

export default router;
