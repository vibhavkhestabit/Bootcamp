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
    group: ["beauty", "fragrances", "skin-care", "skincare"],
  },
  {
    id: "furniture",
    title: "Home Aesthetics",
    group: ["furniture", "home-decoration"],
  },
];

const container = document.getElementById("productContainer");
const loader = document.getElementById("loader");
const searchInput = document.getElementById("searchInput");
const sortSelect = document.getElementById("sortSelect");
const pageTitle = document.getElementById("pageTitle");
const categoryDropdown = document.getElementById("categoryDropdown");
const cartBadge = document.getElementById("cartBadge");

// Sections to toggle
const heroSection = document.getElementById("heroSection");
const controlsSection = document.getElementById("controlsSection");

async function init() {
  try {
    if (window.lucide) lucide.createIcons();
  } catch (e) {}
  updateCartCount();

  try {
    const res = await fetch("https://dummyjson.com/products?limit=100");
    const data = await res.json();
    allProducts = data.products;

    populateDropdown(allProducts);
    loader.classList.add("hidden");

    switchView("home");
  } catch (e) {
    console.error(e);
    container.innerHTML =
      '<div style="text-align:center;">Error loading products.</div>';
  }
}

function switchView(view) {
  currentView = view;
  document
    .querySelectorAll(".filter-btn")
    .forEach((b) => b.classList.remove("active"));

  // Reset Views
  container.innerHTML = "";
  document.getElementById("noResults").classList.add("hidden");

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
    renderCartPage();
  }

  if (window.lucide) lucide.createIcons();
}

// --- RENDER CART PAGE ---
function renderCartPage() {
  container.className = "";

  if (cart.length === 0) {
    container.innerHTML = `
                    <div style="text-align:center; padding: 4rem;">
                        <h2>YOUR CART IS EMPTY</h2>
                        <button onclick="switchView('shop-all')" class="add-btn" style="max-width:200px; margin-top:1rem;">START SHOPPING</button>
                    </div>`;
    return;
  }

  let cartHTML = "";
  let total = 0;

  cart.forEach((item) => {
    total += item.price * item.qty;
    cartHTML += `
                    <div class="cart-page-item">
                        <img src="${
                          item.thumbnail
                        }" class="cart-page-img" alt="${item.title}">
                        <div class="cart-page-info">
                            <div>
                                <div class="cart-page-title">${item.title}</div>
                                <div class="cart-page-meta">${item.category.toUpperCase()}</div>
                                <div class="cart-page-price">$${
                                  item.price
                                }</div>
                            </div>
                            <div class="cart-page-actions">
                                <div class="qty-control-lg">
                                    <button class="qty-btn-lg" onclick="updateQty(${
                                      item.id
                                    }, -1)">-</button>
                                    <div class="qty-val-lg">${item.qty}</div>
                                    <button class="qty-btn-lg" onclick="updateQty(${
                                      item.id
                                    }, 1)">+</button>
                                </div>
                                <div class="remove-link" onclick="removeFromCart(${
                                  item.id
                                })">REMOVE</div>
                            </div>
                        </div>
                    </div>
                `;
  });

  container.innerHTML = `
                <div class="cart-page-wrapper">
                    <div>
                        <div class="cart-list-header">MY SHOPPING BAG (${
                          cart.length
                        })</div>
                        ${cartHTML}
                    </div>
                    <div>
                        <div class="cart-summary-box">
                            <h3 style="margin-bottom:1.5rem; font-size:1.5rem;">ORDER SUMMARY</h3>
                            <div class="summary-row"><span>Subtotal</span> <span>$${total.toFixed(
                              2
                            )}</span></div>
                            <div class="summary-row"><span>Shipping</span> <span>FREE</span></div>
                            <div class="summary-total"><span>TOTAL</span> <span>$${total.toFixed(
                              2
                            )}</span></div>
                            <button class="checkout-btn-lg">PROCEED TO CHECKOUT</button>
                        </div>
                    </div>
                </div>
            `;
}

// --- RENDER HOME ---
function renderHomeHorizontal() {
  container.className = "product-sections-container";

  homeSections.forEach((section) => {
    let sectionProducts = getProductsForSection(section);
    if (sectionProducts.length > 0) {
      const sectionWrapper = document.createElement("div");
      sectionWrapper.className = "category-section";
      let cardsHTML = "";
      sectionProducts.forEach((p) => (cardsHTML += createCardHTML(p)));
      sectionWrapper.innerHTML = `<h2 class="category-section-title">${section.title}</h2><div class="horizontal-scroll">${cardsHTML}</div>`;
      container.appendChild(sectionWrapper);
    }
  });
}

// --- RENDER SHOP ALL ---
function renderShopAllVertical() {
  container.className = "product-sections-container";
  const categories = [...new Set(allProducts.map((p) => p.category))].sort();
  categories.forEach((cat) => {
    const catProducts = allProducts.filter((p) => p.category === cat);
    if (catProducts.length > 0) {
      const sectionWrapper = document.createElement("div");
      sectionWrapper.className = "category-section";
      const displayTitle = cat
        .split("-")
        .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
        .join(" ");
      let cardsHTML = "";
      catProducts.forEach((p) => (cardsHTML += createCardHTML(p)));
      sectionWrapper.innerHTML = `<h2 class="category-section-title">${displayTitle}</h2><div class="product-grid">${cardsHTML}</div>`;
      container.appendChild(sectionWrapper);
    }
  });
}

function getProductsForSection(section) {
  if (section.id === "top-rated") {
    return [...allProducts].sort((a, b) => b.rating - a.rating).slice(0, 10);
  } else {
    return allProducts.filter((p) => {
      if (section.group) return section.group.includes(p.category);
      return p.category === section.id;
    });
  }
}

function createCardHTML(p) {
  const rating = p.rating.toFixed(1);
  const isWishlisted = wishlist.includes(p.id) ? "active" : "";

  return `
                <div class="card">
                    <div class="card-badge">NEW</div>
                    <div class="card-img-container">
                        <img src="${p.thumbnail}" class="card-img" alt="${
    p.title
  }" loading="lazy">
                    </div>
                    <div class="card-details">
                        <div class="card-meta">
                            <span>${p.category.toUpperCase()}</span>
                            <div class="rating-badge">${rating} ★</div>
                        </div>
                        <h4 class="card-title">${p.title}</h4>
                        <div class="price-group">
                            <div class="card-price">$${p.price}</div>
                        </div>
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
                </div>
            `;
}

window.toggleWishlist = (id, btn) => {
  const index = wishlist.indexOf(id);
  if (index === -1) {
    wishlist.push(id);
    btn.classList.add("active");
  } else {
    wishlist.splice(index, 1);
    btn.classList.remove("active");
  }
  localStorage.setItem("ut_wishlist", JSON.stringify(wishlist));
};

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
  } else {
    switchView(currentView);
  }
  if (window.lucide) lucide.createIcons();
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
}

searchInput.addEventListener("input", applyFilters);
sortSelect.addEventListener("change", applyFilters);

function populateDropdown(products) {
  const categories = [...new Set(products.map((p) => p.category))].sort();
  const allLink = document.createElement("a");
  allLink.className = "dropdown-item";
  allLink.textContent = "All Categories";
  allLink.onclick = () => switchView("shop-all");
  categoryDropdown.appendChild(allLink);

  categories.forEach((cat) => {
    const item = document.createElement("a");
    item.className = "dropdown-item";
    item.textContent = cat
      .split("-")
      .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
      .join(" ");
    item.onclick = () => {
      searchInput.value = "";
      renderFlat(allProducts.filter((p) => p.category === cat));
      pageTitle.textContent = item.textContent;
    };
    categoryDropdown.appendChild(item);
  });
}

function addToCart(id, btn) {
  const item = allProducts.find((p) => p.id === id);
  const exist = cart.find((c) => c.id === id);
  if (exist) exist.qty++;
  else cart.push({ ...item, qty: 1 });

  saveCart();
  updateCartCount();

  const originalText = btn.innerText;
  btn.innerText = "ADDED";
  btn.classList.add("added");
  setTimeout(() => {
    btn.innerText = originalText;
    btn.classList.remove("added");
  }, 1000);
}

function removeFromCart(id) {
  cart = cart.filter((c) => c.id !== id);
  saveCart();
  if (currentView === "cart") renderCartPage();
  updateCartCount();
}

function updateQty(id, change) {
  const item = cart.find((c) => c.id === id);
  if (item) {
    item.qty += change;
    if (item.qty <= 0) removeFromCart(id);
    else saveCart();
  }
  if (currentView === "cart") renderCartPage();
  updateCartCount();
}

function saveCart() {
  localStorage.setItem("ut_cart", JSON.stringify(cart));
}

function updateCartCount() {
  const total = cart.reduce((acc, c) => acc + c.qty, 0);
  document.getElementById("cartBadge").innerText = total;
  document.getElementById("cartBadge").classList.toggle("hidden", total === 0);
}

function toggleCart() {
  switchView("cart");
}

init();
