import winston from "winston";
import path from "path";
import { getRequestId } from "./tracing.js";

const logFormat = winston.format.printf(
  ({ level, message, timestamp, requestId }) => {
    const id = requestId ? ` [ID: ${requestId}]` : "";
    return `${timestamp}${id} [${level.toUpperCase()}]: ${message}`;
  }
);

const logger = winston.createLogger({
  level: "info",
  format: winston.format.combine(
    winston.format.timestamp({ format: "YYYY-MM-DD HH:mm:ss" }),
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
    new winston.transports.File({
      filename: path.join("src", "logs", "error.log"),
      level: "error",
    }),
  ],
});

export default logger;