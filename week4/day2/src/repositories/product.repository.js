import Product from "../models/Product.js";

class ProductRepository {
  create(data) {
    return Product.create(data);
  }

  async findAdvanced({ filters = {}, sort = { createdAt: -1 }, page = 1, limit = 20 }) {
    const skip = (page - 1) * limit;

    const [data, total] = await Promise.all([
      Product.find(filters).sort(sort).skip(skip).limit(limit),
      Product.countDocuments(filters)
    ]);

    return { data, total, page, limit };
  }

  softDelete(id) {
    return Product.findByIdAndUpdate(
      id, 
      { deletedAt: new Date() }, 
      { new: true }
    );
  }

  findById(id, includeDeleted = false) {
    const query = { _id: id };
    if (!includeDeleted) query.deletedAt = null;
    return Product.findOne(query);
  }

  update(id, data) {
    return Product.findOneAndUpdate(
      { _id: id, deletedAt: null }, 
      data, 
      { new: true }
    );
  }

  deleteMany(filter) {
    return Product.deleteMany(filter);
  }
}

export default new ProductRepository();