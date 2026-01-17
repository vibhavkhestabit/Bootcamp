let allProducts = [];
let cart = JSON.parse(localStorage.getItem("ut_cart")) || [];
let wishlist = JSON.parse(localStorage.getItem("ut_wishlist")) || [];
let currentView = "home";

const homeSections = [
  { id: "top-rated", title: "Top Rated Picks" },
  {
    id: "watches",
    title: "Vintage Watches",
    group: ["mens-watches", "womens-watches"],
  },
  {
    id: "shoes",
    title: "Streetwear Kicks",
    group: ["mens-shoes", "womens-shoes"],
  },
  {
    id: "beauty",
    title: "Beauty & Care",
    group: ["beauty", "fragrances", "skin-care"],
  },
];

const container = document.getElementById("productContainer");
const loader = document.getElementById("loader");
const searchInput = document.getElementById("searchInput");
const sortSelect = document.getElementById("sortSelect");
const pageTitle = document.getElementById("pageTitle");
const categoryDropdown = document.getElementById("categoryDropdown");
const cartBadge = document.getElementById("cartBadge");
const wishlistBadge = document.getElementById("wishlistBadge");
const heroSection = document.getElementById("heroSection");
const controlsSection = document.getElementById("controlsSection");

async function init() {
  updateBadges();
  try {
    const res = await fetch("https://dummyjson.com/products?limit=100");
    const data = await res.json();
    allProducts = data.products;
    populateDropdown(allProducts);
    loader.classList.add("hidden");
    switchView("home");
  } catch (e) {
    loader.innerHTML = "Error loading products.";
  }
}

function switchView(view) {
  currentView = view;
  container.innerHTML = "";
  document.getElementById("noResults").classList.add("hidden");
  window.scrollTo(0, 0);

  if (document.getElementById("btn-home"))
    document
      .getElementById("btn-home")
      .classList.toggle("active", view === "home");
  if (document.getElementById("btn-shop"))
    document
      .getElementById("btn-shop")
      .classList.toggle("active", view === "shop-all");

  if (view === "home") {
    heroSection.classList.remove("hidden");
    controlsSection.classList.remove("hidden");
    pageTitle.textContent = "Home";
    renderHomeHorizontal();
  } else if (view === "shop-all") {
    heroSection.classList.add("hidden");
    controlsSection.classList.remove("hidden");
    pageTitle.textContent = "Shop All Categories";
    renderShopAllVertical();
  } else if (view === "cart") {
    heroSection.classList.add("hidden");
    controlsSection.classList.add("hidden");
    pageTitle.textContent = "Your Bag";
    renderCartPage();
  } else if (view === "wishlist") {
    heroSection.classList.add("hidden");
    controlsSection.classList.add("hidden");
    pageTitle.textContent = "Your Wishlist";
    renderWishlistPage();
  }
  lucide.createIcons();
}

function renderHomeHorizontal() {
  container.className = "product-sections-container";
  homeSections.forEach((section) => {
    let sectionProducts =
      section.id === "top-rated"
        ? [...allProducts].sort((a, b) => b.rating - a.rating).slice(0, 8)
        : allProducts.filter((p) =>
            section.group
              ? section.group.includes(p.category)
              : p.category === section.id
          );

    if (sectionProducts.length > 0) {
      const div = document.createElement("div");
      div.className = "category-section";
      let cards = "";
      sectionProducts.forEach((p) => (cards += createCardHTML(p)));
      div.innerHTML = `<h2 class="category-section-title">${section.title}</h2><div class="horizontal-scroll">${cards}</div>`;
      container.appendChild(div);
    }
  });
  lucide.createIcons();
}

function renderShopAllVertical() {
  container.className = "product-grid";
  allProducts.forEach((p) => {
    const div = document.createElement("div");
    div.innerHTML = createCardHTML(p);
    container.appendChild(div.firstElementChild);
  });
  lucide.createIcons();
}

function renderWishlistPage() {
  container.className = "product-grid";
  const wishlistItems = allProducts.filter((p) => wishlist.includes(p.id));

  if (wishlistItems.length === 0) {
    container.innerHTML = `<div style="text-align:center; grid-column: 1/-1; padding: 4rem;">
                    <h2>WISHLIST IS EMPTY</h2>
                    <p style="margin: 1rem 0;">Keep track of your favorites here.</p>
                    <button onclick="switchView('shop-all')" class="add-btn" style="max-width:200px; margin: 0 auto;">START SHOPPING</button>
                </div>`;
    return;
  }

  wishlistItems.forEach((p) => {
    const div = document.createElement("div");
    div.innerHTML = createCardHTML(p);
    container.appendChild(div.firstElementChild);
  });
  lucide.createIcons();
}

function createCardHTML(p) {
  const isWishlisted = wishlist.includes(p.id) ? "active" : "";
  return `
                <div class="card">
                    <div class="card-badge">NEW</div>
                    <div class="card-img-container"><img src="${
                      p.thumbnail
                    }" class="card-img" loading="lazy"></div>
                    <div class="card-details">
                        <div class="rating-badge">${p.rating.toFixed(1)} ★</div>
                        <h4 class="card-title">${p.title}</h4>
                        <div class="card-price">$${p.price}</div>
                        <div class="card-actions">
                            <button class="wishlist-btn ${isWishlisted}" onclick="toggleWishlist(${
    p.id
  }, this)">
                                <i data-lucide="heart"></i>
                            </button>
                            <button onclick="addToCart(${
                              p.id
                            }, this)" class="add-btn">ADD TO CART</button>
                        </div>
                    </div>
                </div>`;
}

function toggleWishlist(id, btn) {
  const index = wishlist.indexOf(id);
  if (index === -1) {
    wishlist.push(id);
    btn.classList.add("active");
  } else {
    wishlist.splice(index, 1);
    btn.classList.remove("active");
    if (currentView === "wishlist") renderWishlistPage();
  }
  localStorage.setItem("ut_wishlist", JSON.stringify(wishlist));
  updateBadges();
}

function applyFilters() {
  const search = searchInput.value.toLowerCase().trim();
  const sort = sortSelect.value;

  if (search || sort !== "default") {
    let filtered = [...allProducts];
    if (search)
      filtered = filtered.filter((p) => p.title.toLowerCase().includes(search));
    if (sort === "low") filtered.sort((a, b) => a.price - b.price);
    if (sort === "high") filtered.sort((a, b) => b.price - a.price);
    if (sort === "rating") filtered.sort((a, b) => b.rating - a.rating);

    renderFlat(filtered);
    heroSection.classList.add("hidden");
  } else {
    switchView(currentView);
  }
}

function renderFlat(products) {
  container.innerHTML = "";
  container.className = "product-grid";
  if (!products.length) {
    document.getElementById("noResults").classList.remove("hidden");
    return;
  }
  document.getElementById("noResults").classList.add("hidden");
  products.forEach((p) => {
    const div = document.createElement("div");
    div.innerHTML = createCardHTML(p);
    container.appendChild(div.firstElementChild);
  });
  lucide.createIcons();
}

function populateDropdown(products) {
  const categories = [...new Set(products.map((p) => p.category))].sort();
  categories.forEach((cat) => {
    const a = document.createElement("a");
    a.className = "dropdown-item";
    a.textContent = cat.replace("-", " ");
    a.onclick = () => {
      renderFlat(allProducts.filter((p) => p.category === cat));
      pageTitle.textContent = cat.toUpperCase();
      heroSection.classList.add("hidden");
      window.scrollTo(0, 0);
    };
    categoryDropdown.appendChild(a);
  });
}

function addToCart(id, btn) {
  const item = allProducts.find((p) => p.id === id);
  const exist = cart.find((c) => c.id === id);
  if (exist) exist.qty++;
  else cart.push({ ...item, qty: 1 });

  localStorage.setItem("ut_cart", JSON.stringify(cart));
  updateBadges();

  const oldText = btn.innerText;
  btn.innerText = "ADDED";
  btn.classList.add("added");
  setTimeout(() => {
    btn.innerText = oldText;
    btn.classList.remove("added");
  }, 1000);
}

function updateBadges() {
  const tc = cart.reduce((acc, c) => acc + c.qty, 0);
  cartBadge.innerText = tc;
  cartBadge.classList.toggle("hidden", tc === 0);

  const tw = wishlist.length;
  wishlistBadge.innerText = tw;
  wishlistBadge.classList.toggle("hidden", tw === 0);
}

function updateQty(id, change) {
  const item = cart.find((c) => c.id === id);
  if (item) {
    item.qty += change;
    if (item.qty <= 0) cart = cart.filter((c) => c.id !== id);
    localStorage.setItem("ut_cart", JSON.stringify(cart));
    renderCartPage();
    updateBadges();
  }
}

function renderCartPage() {
  if (cart.length === 0) {
    container.innerHTML = `<div style="text-align:center; grid-column: 1/-1; padding: 4rem;"><h2>BAG IS EMPTY</h2><button onclick="switchView('shop-all')" class="add-btn" style="max-width:200px; margin:2rem auto;">SHOP NOW</button></div>`;
    return;
  }
  let total = 0;
  let cartHTML = `<div class="cart-page-wrapper"><div>`;
  cart.forEach((item) => {
    total += item.price * item.qty;
    cartHTML += `
                    <div class="cart-page-item">
                        <img src="${item.thumbnail}" class="cart-page-img">
                        <div style="flex-grow:1">
                            <h4 style="margin-bottom: 0.5rem;">${item.title}</h4>
                            <p style="font-weight: 700; margin-bottom: 1rem;">$${item.price}</p>
                            <div style="display:flex; align-items:center; gap: 1rem; margin-top: auto;">
                                <div style="display:flex; align-items:center; border: 1px solid black;">
                                    <button onclick="updateQty(${item.id}, -1)" style="padding:5px 15px; background: white; border: none; cursor:pointer;">-</button>
                                    <span style="padding:0 15px; font-weight: 700;">${item.qty}</span>
                                    <button onclick="updateQty(${item.id}, 1)" style="padding:5px 15px; background: white; border: none; cursor:pointer;">+</button>
                                </div>
                                <button onclick="updateQty(${item.id}, -${item.qty})" style="background: none; border: none; text-decoration: underline; font-size: 0.8rem; cursor:pointer; color: #ef4444;">Remove</button>
                            </div>
                        </div>
                    </div>`;
  });
  cartHTML += `</div><div class="cart-summary-box">
                <h3 style="margin-bottom: 1rem;">SUMMARY</h3>
                <div style="display:flex; justify-content: space-between; margin-bottom: 1rem;"><span>Subtotal</span><span>$${total.toFixed(
                  2
                )}</span></div>
                <div style="display:flex; justify-content: space-between; margin-bottom: 1rem; color: #10b981;"><span>Shipping</span><span>FREE</span></div>
                <div style="display:flex; justify-content: space-between; padding-top: 1rem; border-top: 2px solid black; font-size: 1.5rem; font-weight: 700;"><span>TOTAL</span><span>$${total.toFixed(
                  2
                )}</span></div>
                <button class="add-btn" style="width:100%; margin-top:2rem;">CHECKOUT</button>
            </div></div>`;
  container.innerHTML = cartHTML;
}

searchInput.addEventListener("input", applyFilters);
sortSelect.addEventListener("change", applyFilters);
init();
