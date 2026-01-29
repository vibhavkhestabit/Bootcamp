import mongoose from "mongoose";
import bcrypt from "bcrypt";

const userSchema = new mongoose.Schema(
  {
    firstName: {
      type: String,
      required: true,
      trim: true,
    },

    lastName: {
      type: String,
      required: true,
      trim: true,
    },

    email: {
      type: String,
      required: true,
      unique: true,
      lowercase: true,
      index: true,
    },

    password: {
      type: String,
      required: true,
      select: false,
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
    toObject: { virtuals: true },
  }
);

/* 🔹 Pre-save hook (hash password) */
userSchema.pre("save", async function () {
  if (!this.isModified("password")) return next();

  this.password = await bcrypt.hash(this.password, 10);
});

/* 🔹 Virtual field */
userSchema.virtual("fullName").get(function () {
  return `${this.firstName} ${this.lastName}`;
});

/* 🔹 Compound index */
userSchema.index({ status: 1, createdAt: -1 });

export default mongoose.model("User", userSchema);
