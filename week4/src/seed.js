import connectDB from "./loaders/db.js";
import UserRepository from "./repositories/user.repository.js";
import ProductRepository from "./repositories/product.repository.js";

async function test() {
  await connectDB();

  /* 🔹 Create User */
  const user = await UserRepository.create({
    firstName: "Vibhav",
    lastName: "Khaneja",
    email: "vibhav.khaneja@hestabit.in",
    password: "Helloooooo",
  });

  console.log("USER CREATED:", user);

   const user2 = await UserRepository.create({
    firstName: "Samarth",
    lastName: "Singh",
    email: "Sam@gmail.com",
    password: "Samsung",
  });

  console.log("USER CREATED:", user2);

  /* 🔹 Fetch User */
  const fetchedUser = await UserRepository.findById(user._id);
  console.log("USER FETCHED:", fetchedUser);

  const fetchedUser2 = await UserRepository.findById(user2._id);
  console.log("USER FETCHED:", fetchedUser2);

  /* 🔹 Create Product */
  const product = await ProductRepository.create({
    name: "Laptop",
    price: 1500,
    createdBy: user._id
  });

  console.log("PRODUCT CREATED:", product);

    const product2 = await ProductRepository.create({
    name: "iPhone",
    price: 4500,
    createdBy: user2._id
  });

  console.log("PRODUCT CREATED:", product2);

  process.exit(0);
}

test().catch(console.error);
