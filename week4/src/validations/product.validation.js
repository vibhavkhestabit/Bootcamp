import Joi from "joi";

const objectId = Joi.string().hex().length(24);

export const createProductSchema = {
  body: Joi.object({
    name: Joi.string().trim().min(2).max(100).required(),
    price: Joi.number().min(0).required(),
    rating: Joi.number().min(0).max(5).optional(),
    status: Joi.string().valid("active", "inactive").optional(),
    createdBy: objectId.required(),
  }),
};

export const listProductSchema = {
  query: Joi.object({
    search: Joi.string().trim().allow(""),
    minPrice: Joi.number().min(0),
    maxPrice: Joi.number().min(0),
    sort: Joi.string().pattern(/^[a-zA-Z]+:(asc|desc)$/),
    page: Joi.number().integer().min(1).default(1),
    limit: Joi.number().integer().min(1).max(100).default(20),
    includeDeleted: Joi.boolean().default(false),
  }),
};

export const updateProductSchema = {
  body: Joi.object({
    name: Joi.string().trim().min(2).max(100),
    price: Joi.number().min(0),
    rating: Joi.number().min(0).max(5),
    status: Joi.string().valid("active", "inactive"),
  }).min(1),
};
