import express from "express";
import routes from "../routes/index.js";
import applySecurity from "../middlewares/security.js";
import errorMiddleware from "../middlewares/error.middleware.js";
import { tracingMiddleware } from "../utils/tracing.js"; // New import
import logger from "../utils/logger.js"; // New import

export default function loadApp() {
  const app = express();

  // 1. MUST BE FIRST: Assign IDs to every request
  app.use(tracingMiddleware);

  // 2. Request Logging: Log every incoming request with its Trace ID
  app.use((req, res, next) => {
    logger.info(`${req.method} ${req.url}`);
    next();
  });

  // Body parser (limit enforced)
  app.use(express.json({ limit: "10kb" }));

  // SECURITY layer (Helmet, CORS, XSS, mongo-sanitize, rate-limit)
  applySecurity(app);

  // Routes
  app.use("/api", routes);

  // Global error handler
  app.use(errorMiddleware);

  return app;
}