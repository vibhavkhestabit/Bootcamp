import path from "path";
import dotenv from "dotenv";
import logger from "../utils/logger.js";

const NODE_ENV = process.env.environment || ".env.local";

// const envFileMap = {
//   local: ".env.local",
//   dev: ".env.dev",
//   prod: ".env.prod",
// };

const envFile = NODE_ENV;

if (!envFile) {
  const errorMsg = `Invalid NODE_ENV: ${NODE_ENV}`;
  console.error(errorMsg); 
  throw new Error(errorMsg);
}

dotenv.config({
  path: path.resolve(process.cwd(), envFile),
});

logger.info(`Environment Config loaded from ${envFile}`);

const requiredEnvVars = ["PORT", "DB_URI"];

requiredEnvVars.forEach((key) => {
  if (!process.env[key]) {
    const errorMsg = `Missing required environment variable: ${key}`;
    logger.error(errorMsg);
    throw new Error(errorMsg);
  }
});

const config = {
  env: NODE_ENV,
  port: Number(process.env.PORT),
  dbUri: process.env.DB_URI,
  logLevel: process.env.LOG_LEVEL || "info",
};

export default config;