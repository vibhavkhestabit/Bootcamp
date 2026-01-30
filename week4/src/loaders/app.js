import express from "express";
import routes from "../routes/index.js";
import { globalErrorHandler } from "../middlewares/error.middleware.js";

export default function loadApp() {
  const app = express();
  app.use(express.json());

  app.use("/api", routes);

  // 🔹 The Error Boundary (Must be after routes)
  app.use(globalErrorHandler); 

  return app;
}