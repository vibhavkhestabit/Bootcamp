/**
 * 1. What it is: Redis Configuration Module.
 * 2. Why: Centralizes connection logic for BullMQ and Caching.
 * 3. How: Exports a standardized connection object used by Workers and Producers.
 */
const redisConfig = {
  host: process.env.REDIS_HOST || "127.0.0.1",
  port: Number(process.env.REDIS_PORT) || 6379,
  password: process.env.REDIS_PASSWORD || null,
  // Required for BullMQ to handle stalled jobs correctly
  maxRetriesPerRequest: null, 
};

export default redisConfig;