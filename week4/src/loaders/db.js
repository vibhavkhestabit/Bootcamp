import mongoose from "mongoose";
import config from "../config/index.js";
import logger from "../utils/logger.js";

export default async function connectDB() {
  try {
    await mongoose.connect(config.dbUri);
    logger.info("Database connected");
  } catch (error) {
    logger.error("Database connection failed");
    throw error; // ❗ app must not start
  }
}