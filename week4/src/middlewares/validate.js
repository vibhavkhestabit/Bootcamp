import Joi from "joi";

const validate = (schema, property = "body") => {
  return (req, res, next) => {
    const { error, value } = schema.validate(req[property], {
      abortEarly: false,
      stripUnknown: true,
    });

    if (error) {
      return next({
        statusCode: 400,
        message: "Validation failed",
        code: "VALIDATION_ERROR",
        details: error.details.map(d => d.message),
      });
    }

    req[property] = value; // sanitized input
    next();
  };
};

export default validate;
