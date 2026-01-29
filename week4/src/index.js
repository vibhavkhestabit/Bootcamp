import config from "./config/index.js";
import logger from "./utils/logger.js";
import connectDB from "./loaders/db.js";
import loadApp from "./loaders/app.js";

async function startServer() {
  try {
    await connectDB();

    const app = loadApp();

    app.listen(config.port, () => {
      logger.info(`Server started on port ${config.port}`);
    });
  } catch (error) {
    logger.error("Server startup failed");
    process.exit(1);
  }
}

startServer();
