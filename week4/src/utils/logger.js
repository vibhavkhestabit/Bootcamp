import winston from "winston";
import path from "path";

const logFormat = winston.format.printf(
  ({ level, message, timestamp }) => {
    return `${timestamp} [${level.toUpperCase()}]: ${message}`;
  }
);

const logger = winston.createLogger({
  level: "info",
  format: winston.format.combine(
    winston.format.timestamp(),
    logFormat
  ),
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({
      filename: path.join("src", "logs", "app.log"),
    }),
  ],
});

export default logger;
