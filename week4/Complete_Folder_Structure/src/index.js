import config from "./config/index.js";
import logger from "./utils/logger.js";
import connectDB from "./loaders/db.js";
import loadApp from "./loaders/app.js";
import "./jobs/email.job.js"; 

async function startServer() {
  logger.info("--- Backend Boot Sequence Initiated ---");
  
  try {
    logger.info("Connecting to Database...");
    await connectDB();
  
    logger.info("Loading Express Application...");
    const app = loadApp();

    app.listen(config.port, () => {
      logger.info(` Server successfully started on port ${config.port}`);
      logger.info(`--- Mode: ${config.env} ---`);
    });
  } catch (error) {
    logger.error(` Server startup failed: ${error.message}`);
    process.exit(1);
  }
}

startServer();