import ProductRepository from "../repositories/product.repository.js";
import AppError from "../utils/appError.js";

class ProductService {
  async createProduct(data) {
    if (!data.name || !data.price) {
      throw new AppError("Name and Price are required", 400, "VALIDATION_ERROR");
    }
    return await ProductRepository.create(data);
  }

  async getAllProducts(query) {
    const { search, minPrice, maxPrice, sort, page, limit, includeDeleted } = query;
    const filters = {};

    // 1. Regex Search (Case-insensitive)
    if (search) filters.name = { $regex: search, $options: "i" };

    // 2. Range Filters
    if (minPrice || maxPrice) {
      filters.price = {};
      if (minPrice) filters.price.$gte = Number(minPrice);
      if (maxPrice) filters.price.$lte = Number(maxPrice);
    }

    // 3. Soft Delete logic
    if (includeDeleted !== "true") filters.deletedAt = null;

    // 4. Sort parsing (e.g., "price:desc")
    let sortObj = { createdAt: -1 };
    if (sort) {
      const [field, order] = sort.split(":");
      sortObj = { [field]: order === "desc" ? -1 : 1 };
    }

    return await ProductRepository.findAdvanced({
      filters,
      sort: sortObj,
      page: Number(page) || 1,
      limit: Number(limit) || 10
    });
  }

  async updateProduct(id, data) {
    const product = await ProductRepository.update(id, data);
    if (!product) throw new AppError("Product not found", 404, "NOT_FOUND");
    return product;
  }

  async softDeleteProduct(id) {
    const product = await ProductRepository.softDelete(id);
    if (!product) throw new AppError("Product not found", 404, "NOT_FOUND");
    return product;
  }
}

export default new ProductService();