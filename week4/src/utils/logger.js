import winston from "winston";
import path from "path";
import { getRequestId } from "./tracing.js";

/**
 * 1. What it is: A Custom Log Formatter.
 * 2. Why: To inject the Request ID (Correlation ID) into every log line.
 * 3. How: It pulls the ID from AsyncLocalStorage and prepends it to the message.
 */
const logFormat = winston.format.printf(
  ({ level, message, timestamp, requestId }) => {
    // If a requestId exists, we display it in brackets, otherwise leave it blank
    const id = requestId ? ` [ID: ${requestId}]` : "";
    return `${timestamp}${id} [${level.toUpperCase()}]: ${message}`;
  }
);

const logger = winston.createLogger({
  level: "info",
  format: winston.format.combine(
    winston.format.timestamp({ format: "YYYY-MM-DD HH:mm:ss" }),
    // This custom format "grabs" the ID right before printing
    winston.format((info) => {
      info.requestId = getRequestId(); 
      return info;
    })(),
    logFormat
  ),
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({
      filename: path.join("src", "logs", "app.log"),
    }),
    // Separate file for errors to make debugging faster
    new winston.transports.File({
      filename: path.join("src", "logs", "error.log"),
      level: "error",
    }),
  ],
});

export default logger;