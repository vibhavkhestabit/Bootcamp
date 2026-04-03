import { Queue, Worker } from 'bullmq';
import IORedis from 'ioredis';
import redisConfig from '../config/redis.js';
import logger from '../utils/logger.js';

const connection = new IORedis(redisConfig);

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

export const emailWorker = new Worker(
  'emailNotifications',
  async (job) => {
    const { email, subject } = job.data;

    logger.info(`[Worker] Starting email job ${job.id} for recipient: ${email}`);

    await new Promise((resolve, reject) => {
      setTimeout(() => {
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

emailWorker.on('completed', (job) => {
  logger.info(`Job ${job.id} (Email) has successfully completed.`);
});

emailWorker.on('failed', (job, err) => {
  logger.error(`Job ${job.id} (Email) failed: ${err.message}. Retries remaining: ${job.opts.attempts - job.attemptsMade}`);
});