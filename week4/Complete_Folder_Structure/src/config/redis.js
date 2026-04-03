import logger from "../utils/logger.js";

const redisConfig = {
  host: process.env.REDIS_HOST || "127.0.0.1",
  port: Number(process.env.REDIS_PORT) || 6379,
  password: process.env.REDIS_PASSWORD || null,
  maxRetriesPerRequest: null, 
};

logger.info(`Redis Configuration initialized for ${redisConfig.host}:${redisConfig.port}`);

export default redisConfig;