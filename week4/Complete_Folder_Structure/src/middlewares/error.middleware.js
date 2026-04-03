const errorMiddleware = (err, req, res, next) => {
  const statusCode = err.statusCode || 500;

  res.status(statusCode).json({
    success: false,
    message: err.message || "Internal Server Error",
    code: err.code || "INTERNAL_ERROR",
    timestamp: new Date().toISOString(),
    path: req.originalUrl,
    ...(err.details && { details: err.details }),
  });
};

export default errorMiddleware;
