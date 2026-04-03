import { v4 as uuidv4 } from 'uuid';
import { AsyncLocalStorage } from 'async_hooks';

export const requestIdStorage = new AsyncLocalStorage();

export const tracingMiddleware = (req, res, next) => {
  const requestId = req.headers['x-request-id'] || uuidv4();
  
  res.setHeader('x-request-id', requestId);

  requestIdStorage.run(requestId, () => {
    next();
  });
};

export const getRequestId = () => requestIdStorage.getStore();