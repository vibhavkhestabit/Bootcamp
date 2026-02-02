import ProductService from "../services/product.service.js";

// 🔹 CREATE
export const createProduct = async (req, res) => {
  const product = await ProductService.createProduct(req.body);

  res.status(201).json({
    success: true,
    data: product,
  });
};

// 🔹 READ (With Query Engine)
export const getProducts = async (req, res) => {
  const result = await ProductService.getAllProducts(req.query);

  res.status(200).json({
    success: true,
    ...result,
  });
};

// 🔹 UPDATE
export const updateProduct = async (req, res) => {
  const product = await ProductService.updateProduct(
    req.params.id,
    req.body
  );

  res.status(200).json({
    success: true,
    data: product,
  });
};

// 🔹 DELETE (Soft Delete)
export const deleteProduct = async (req, res) => {
  await ProductService.softDeleteProduct(req.params.id);

  res.status(200).json({
    success: true,
    message: "Product moved to trash",
  });
};
