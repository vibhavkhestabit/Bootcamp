import User from "../models/User.js";

class UserRepository {
  create(data) {
    return User.create(data);
  }

  findById(id) {
    return User.findById(id);
  }

  findPaginated({ page = 1, limit = 10 }) {
    const skip = (page - 1) * limit;

    return User.find()
      .sort({ createdAt: -1 })
      .skip(skip)
      .limit(limit);
  }

  update(id, data) {
    return User.findByIdAndUpdate(id, data, { new: true });
  }

  delete(id) {
    return User.findByIdAndDelete(id);
  }
}

export default new UserRepository();
