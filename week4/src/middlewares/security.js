import helmet from "helmet";
import cors from "cors";
import rateLimit from "express-rate-limit";
import express from "express";

const applySecurity = (app) => {
  // 🔒 Security headers
  app.use(helmet());

  // 🌍 CORS policy
  app.use(
    cors({
      origin: ["http://localhost:3000"], // adjust for prod
      methods: ["GET", "POST", "PATCH", "DELETE"],
      credentials: true,
    })
  );

  // 📦 Payload size limit
  app.use(express.json({ limit: "10kb" }));

  // 🚦 Rate limiting
  const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100,
    standardHeaders: true,
    legacyHeaders: false,
    message: {
      success: false,
      message: "Too many requests, please try again later",
      code: "RATE_LIMIT_EXCEEDED",
    },
  });

  app.use(limiter);
};

export default applySecurity;
