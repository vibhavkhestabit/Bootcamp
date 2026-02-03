import ProductService from "../services/product.service.js";

/**
 * POST /api/products
 */
export const createProduct = async (req, res, next) => {
  const product = await ProductService.createProduct(req.validated.body);
  res.status(201).json({ success: true, data: product });
};

/**
 * GET /api/products
 */
export const getProducts = async (req, res, next) => {
  const result = await ProductService.getAllProducts(req.validated.query);
  res.status(200).json({ success: true, ...result });
};

/**
 * PATCH /api/products/:id
 */
export const updateProduct = async (req, res, next) => {
  const product = await ProductService.updateProduct(
    req.params.id,
    req.validated.body
  );
  res.status(200).json({ success: true, data: product });
};

/**
 * DELETE /api/products/:id
 */
export const deleteProduct = async (req, res, next) => {
  await ProductService.softDeleteProduct(req.params.id);
  res.status(200).json({ success: true, message: "Product moved to trash" });
};
