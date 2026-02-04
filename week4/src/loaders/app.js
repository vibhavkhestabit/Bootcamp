import express from "express";
import routes from "../routes/index.js";
import applySecurity from "../middlewares/security.js";
import errorMiddleware from "../middlewares/error.middleware.js";
import { tracingMiddleware } from "../utils/tracing.js";
import logger from "../utils/logger.js";

export default function loadApp() {
  const app = express();

  logger.info("Initializing Tracing and Request Logging Middlewares...");
  app.use(tracingMiddleware);

  app.use((req, res, next) => {
    logger.info(`${req.method} ${req.url}`);
    next();
  });

  app.use(express.json({ limit: "10kb" }));

  logger.info("Applying Security Layers (Helmet, CORS, Rate-Limit)...");
  applySecurity(app);

  logger.info("Mounting API Routes on /api...");
  app.use("/api", routes);

  logger.info("Loading Global Error Handler...");
  app.use(errorMiddleware);

  return app;
}