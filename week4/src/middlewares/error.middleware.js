export const globalErrorHandler = (err, req, res, next) => {
  err.statusCode = err.statusCode || 500;
  
  res.status(err.statusCode).json({
    success: false,
    message: err.message,
    code: err.errorCode || "INTERNAL_ERROR",
    timestamp: new Date().toISOString(),
    path: req.originalUrl
  });
};