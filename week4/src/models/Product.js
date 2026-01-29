import mongoose from "mongoose";

const productSchema = new mongoose.Schema(
  {
    name: {
      type: String,
      required: true,
      trim: true,
    },

    price: {
      type: Number,
      required: true,
      min: 0,
    },

    rating: {
      type: Number,
      default: 0,
    },

    status: {
      type: String,
      enum: ["active", "inactive"],
      default: "active",
      index: true,
    },
  },
  {
    timestamps: true,
    toJSON: { virtuals: true },
  }
);

/* 🔹 Virtual field */
productSchema.virtual("isExpensive").get(function () {
  return this.price > 1000;
});

/* 🔹 Compound index */
productSchema.index({ status: 1, createdAt: -1 });

export default mongoose.model("Product", productSchema);
