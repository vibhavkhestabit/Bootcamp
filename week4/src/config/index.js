import path from "path";
import dotenv from "dotenv";

const NODE_ENV = process.env.environment|| "local";

const envFileMap = {
  local: ".env.local",
  dev: ".env.dev",
  prod: ".env.prod",
};

const envFile = envFileMap[NODE_ENV];

if (!envFile) {
  throw new Error(`Invalid NODE_ENV: ${NODE_ENV}`);
}

dotenv.config({
  path: path.resolve(process.cwd(), envFile),
});

const requiredEnvVars = ["PORT", "DB_URI"];

requiredEnvVars.forEach((key) => {
  if (!process.env[key]) {
    throw new Error(`Missing required environment variable: ${key}`);
  }
});

const config = {
  env: NODE_ENV,
  port: Number(process.env.PORT),
  dbUri: process.env.DB_URI,
};

export default config;
