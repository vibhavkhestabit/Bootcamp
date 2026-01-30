import Product from "../models/Product.js";

class ProductRepository {
  create(data) {
    return Product.create(data);
  }

  findById(id) {
    return Product.findById(id);
  }

  findPaginated({ page = 1, limit = 10 }) {
    const skip = (page - 1) * limit;

    return Product.find()
      .sort({ createdAt: -1 })
      .skip(skip)
      .limit(limit);
  }

  update(id, data) {
    return Product.findByIdAndUpdate(id, data, { new: true });
  }

  delete(id) {
    return Product.findByIdAndDelete(id);
  }
  deleteMany(filter) {
    return User.deleteMany(filter);
  }
}

export default new ProductRepository();
