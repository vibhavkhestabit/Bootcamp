import mongoose from "mongoose";

const ProductSchema = new mongoose.Schema({
  name: {
    type: String,
    required: [true, "Please enter product name"],
    trim: true,
  },
  brand: {
    type: String,
    required: true,
    enum: [
      "Nike",
      "Adidas",
      "Puma",
      "Reebok",
      "Vans",
      "Converse",
      "New Balance",
      "Other",
    ],
  },
  price: {
    type: Number,
    required: [true, "Price is required"],
  },
  size: {
    type: Number,
    required: true,
  },
  image: {
    type: String,
    required: true,
  },
  condition: {
    type: String,
    enum: ["New", "Refurbished"],
    default: "New",
  },
  age: {
    type: String,
    required: function () {
      return this.condition === "Refurbished";
    },
  },
  description: {
    type: String,
    default: "No description provided.",
  },

  rating: { 
        type: Number, 
        default: 0, 
        min: 0, 
        max: 5 
    },
    isDeleted: { 
        type: Boolean, 
        default: false 
    },
    
  createdAt: {
    type: Date,
    default: Date.now,
  },
});

export default mongoose.model("Product", ProductSchema);
