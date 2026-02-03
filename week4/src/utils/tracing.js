import { v4 as uuidv4 } from 'uuid';
import { AsyncLocalStorage } from 'async_hooks';

// The 'storage' instance that holds the Request ID for the duration of the async flow
export const requestIdStorage = new AsyncLocalStorage();

/**
 * Middleware to assign a unique X-Request-ID to every incoming request.
 */
export const tracingMiddleware = (req, res, next) => {
  const requestId = req.headers['x-request-id'] || uuidv4();
  
  // Set the ID in the response header so the client knows their trace ID
  res.setHeader('x-request-id', requestId);

  // Run the rest of the request inside the storage context
  requestIdStorage.run(requestId, () => {
    next();
  });
};

/**
 * Helper to get the current Request ID anywhere in the service layer
 */
export const getRequestId = () => requestIdStorage.getStore();