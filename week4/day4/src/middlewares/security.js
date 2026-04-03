import helmet from "helmet";
import cors from "cors";
import rateLimit from "express-rate-limit";
import hpp from "hpp";

const applySecurity = (app) => {

  
  app.use(helmet());

  
  const corsOptions = {
    origin: "http://localhost:3000",
    methods: ["GET", "POST", "PUT", "PATCH", "DELETE"],
    allowedHeaders: ["Content-Type", "Authorization"],
    credentials: true,
    maxAge: 46800,
  };
  app.use(cors(corsOptions));


  const limiter = rateLimit({
    windowMs: 15 * 60 * 1000,
    max: 100,
    message: {
      success: false,
      message: "Too many requests from this IP, please try again after 15 minutes",
      code: 429,
    },
    standardHeaders: true,
    legacyHeaders: false,
  });
  app.use("/api", limiter);


  app.use(
    hpp({
      whitelist: ["price", "category", "rating", "tags"],
    })
  );


  app.use((req, res, next) => {
    
    if (req.body && typeof req.body === 'object') {
      const cleanBody = sanitizeXSS(sanitizeObject(req.body));
      for (const key in req.body) delete req.body[key];
      Object.assign(req.body, cleanBody);
    }
    
    
    if (req.params && typeof req.params === 'object') {
      const cleanParams = sanitizeXSS(sanitizeObject(req.params));
      Object.assign(req.params, cleanParams);
    }


    if (req.query && typeof req.query === 'object') {
      const cleanQuery = sanitizeXSS(sanitizeObject(req.query));
      for (const key in req.query) delete req.query[key];
      Object.assign(req.query, cleanQuery);
    }
    
    next();
  });
};


export const validate = (schema) => (req, res, next) => {
  const parts = ["body", "query", "params"];
  
  for (const part of parts) {
    if (schema[part]) {
      const { error, value } = schema[part].validate(req[part], {
        abortEarly: false,
        stripUnknown: true, 
      });

      if (error) {
        const errorMessage = error.details.map((details) => details.message).join(", ");
        return res.status(400).json({ success: false, message: errorMessage });
      }
      
      for (const key in req[part]) delete req[part][key];
      Object.assign(req[part], value);
    }
  }
  next();
};


function sanitizeObject(obj) {
  if (obj === null || typeof obj !== "object") {
    return obj;
  }

  if (Array.isArray(obj)) {
    return obj.map((item) => sanitizeObject(item));
  }

  const sanitized = {};
  for (const key of Object.keys(obj)) {
    if (key.startsWith("$")) continue;
    sanitized[key] = sanitizeObject(obj[key]);
  }
  return sanitized;
}


function sanitizeXSS(obj) {
  if (typeof obj === "string") {
    return obj
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#x27;")
      .replace(/\//g, "&#x2F;");
  }

  if (obj === null || typeof obj !== "object") {
    return obj;
  }

  if (Array.isArray(obj)) {
    return obj.map((item) => sanitizeXSS(item));
  }

  const sanitized = {};
  for (const key of Object.keys(obj)) {
    sanitized[key] = sanitizeXSS(obj[key]);
  }
  return sanitized;
}

export default applySecurity;