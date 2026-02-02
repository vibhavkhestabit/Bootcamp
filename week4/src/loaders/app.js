import express from "express";
import routes from "../routes/index.js";
import applySecurity from "../middlewares/security.js";
import errorMiddleware from "../middlewares/error.middleware.js";

export default function loadApp() {
  const app = express();

  // 🔹 Payload parsing (limit handled inside security as well)
  app.use(express.json({ limit: "10kb" }));

  // 🔹 SECURITY LAYER (Helmet, CORS, Rate Limit)
  applySecurity(app);

  // 🔹 Routes
  app.use("/api", routes);

  // 🔹 Global Error Boundary (MUST be last)
  app.use(errorMiddleware);

  return app;
}
