import express from "express";
import routes from "../routes/index.js";
import applySecurity from "../middlewares/security.js";
import errorMiddleware from "../middlewares/error.middleware.js";

export default function loadApp() {
  const app = express();

  // SECURITY layer (Helmet, CORS, XSS, mongo-sanitize, rate-limit)
 

  // Body parser (limit enforced)
  app.use(express.json({ limit: "10kb" }));

  applySecurity(app);

  // Routes
  app.use("/api", routes);

  // Global error handler
  app.use(errorMiddleware);

  return app;
}
