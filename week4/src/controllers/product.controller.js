import ProductService from "../services/product.service.js";
import { emailQueue } from "../jobs/email.job.js";
import logger from "../utils/logger.js";

/**
 * POST /api/products
 */
export const createProduct = async (req, res, next) => {
  try {
    // 1. Core Logic
    const product = await ProductService.createProduct(req.validated.body);
    
    // 2. Structured Logging (Automatically includes Request ID)
    logger.info(`Product created: ${product._id} by user: ${req.user?.id || 'anonymous'}`);

    // 3. Background Job: Notify Admin/Marketing about new product
    // We add to queue and move on; we don't wait for the email to actually send.
    await emailQueue.add("new-product-alert", {
      email: "inventory@store.com",
      subject: "New Catalog Item",
      body: `A new product "${product.name}" has been added.`
    });

    res.status(201).json({ success: true, data: product });
  } catch (error) {
    next(error);
  }
};

/**
 * GET /api/products
 */
export const getProducts = async (req, res, next) => {
  try {
    logger.info(`Fetching products with query: ${JSON.stringify(req.validated.query)}`);
    const result = await ProductService.getAllProducts(req.validated.query);
    res.status(200).json({ success: true, ...result });
  } catch (error) {
    next(error);
  }
};

/**
 * PATCH /api/products/:id
 */
export const updateProduct = async (req, res, next) => {
  try {
    const product = await ProductService.updateProduct(
      req.params.id,
      req.validated.body
    );
    logger.info(`Product updated: ${req.params.id}`);
    res.status(200).json({ success: true, data: product });
  } catch (error) {
    next(error);
  }
};

/**
 * DELETE /api/products/:id
 */
export const deleteProduct = async (req, res, next) => {
  try {
    await ProductService.softDeleteProduct(req.params.id);
    
    logger.warn(`Product soft-deleted: ${req.params.id}`);
    
    // Background Job: Clean up related cached resources or notify logistics
    await emailQueue.add("product-deletion-log", {
      email: "audit@store.com",
      subject: "Product Archival",
      body: `Product ID ${req.params.id} was moved to trash.`
    });

    res.status(200).json({ success: true, message: "Product moved to trash" });
  } catch (error) {
    next(error);
  }
};