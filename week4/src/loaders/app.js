import express from "express";
import logger from "../utils/logger.js";
import routes from "../routes/index.js";

export default function loadApp() {
  const app = express();

  // Global middlewares
  app.use(express.json());
  app.use(express.urlencoded({ extended: true }));

  app.get("/health", (req, res) => {
  res.status(200).send("ok");
  });

  logger.info("Middlewares loaded");

  // Routes
  app.use("/api", routes);

  logger.info("Routes mounted");

  return app;
}
