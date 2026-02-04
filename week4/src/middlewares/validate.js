import Joi from 'joi';
import AppError from '../utils/appError.js';


const validate = (schema) => {
  return (req, res, next) => {
    const toValidate = {};
    
    if (schema.body && req.body) toValidate.body = req.body;
    if (schema.query && req.query) toValidate.query = req.query;
    if (schema.params && req.params) toValidate.params = req.params;

    const validationSchema = Joi.object({
      body: schema.body || Joi.any(),
      query: schema.query || Joi.any(),
      params: schema.params || Joi.any(),
    });

    const { error, value } = validationSchema.validate(toValidate, {
      abortEarly: false,
      stripUnknown: true,
      errors: { label: 'key' },
    });

    if (error) {
      const errorMessage = error.details.map(d => d.message).join(', ');
      return next(new AppError(errorMessage, 400, "VALIDATION_ERROR"));
    }

    if (!req.validated) req.validated = {};
    if (value.body) req.validated.body = value.body;
    if (value.query) req.validated.query = value.query;
    if (value.params) req.validated.params = value.params;

    next();
  };
};

export default validate;
