import { Queue, Worker } from 'bullmq';
import IORedis from 'ioredis';
import redisConfig from '../config/redis.js';
import logger from '../utils/logger.js';

/**
 * 1. What it is: A Background Job Processor.
 * 2. Why: To handle time-consuming tasks like email without blocking the API response.
 * 3. How: Using BullMQ and Redis to manage a queue and a worker process.
 */

// 1. Establish Redis Connection using modular config
const connection = new IORedis(redisConfig);

// 2. Initialize the Queue (The Producer)
export const emailQueue = new Queue('emailNotifications', {
  connection,
  defaultJobOptions: {
    attempts: 3, 
    backoff: {
      type: 'exponential',
      delay: 2000, 
    },
    removeOnComplete: true, 
  },
});

// 3. Initialize the Worker (The Consumer)
export const emailWorker = new Worker(
  'emailNotifications',
  async (job) => {
    const { email, subject } = job.data;

    // Use structured logger instead of console.log
    logger.info(`[Worker] Starting email job ${job.id} for recipient: ${email}`);

    // Simulation of an email service
    await new Promise((resolve, reject) => {
      setTimeout(() => {
        // Randomly simulate a failure to test the Retry + Backoff logic
        if (Math.random() > 0.9) {
          return reject(new Error("SMTP Connection Timeout"));
        }
        
        logger.info(`[Worker] Email payload delivered for job ${job.id}`);
        resolve();
      }, 1500);
    });
  },
  { connection }
);

// Listeners for monitoring using structured logging
emailWorker.on('completed', (job) => {
  logger.info(`Job ${job.id} (Email) has successfully completed.`);
});

emailWorker.on('failed', (job, err) => {
  logger.error(`Job ${job.id} (Email) failed: ${err.message}. Retries remaining: ${job.opts.attempts - job.attemptsMade}`);
});