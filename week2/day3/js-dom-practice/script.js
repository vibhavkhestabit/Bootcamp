lucide.createIcons();

const modal = document.getElementById("modal");
const modalBox = document.getElementById("modalBox");
const accordion = document.getElementById("accordion");
const sortDropdown = document.getElementById("sortDropdown");
//Storing DOM elements as variables in these steps

document.querySelectorAll(".accordion-header").forEach(header => {
  header.addEventListener("click", () => {
    const item = header.parentElement;
    const icon = header.querySelector("svg");

//Here we are providing it the fucntionality to open and close the accordian

    item.classList.toggle("active");

    icon.setAttribute(
      "data-lucide",
      item.classList.contains("active") ? "minus" : "plus"
    );
  //Here we are using Set Attribute to convert our lucide Plus symbol to lucide Minus Symbol whenever it is being popped open
    lucide.createIcons();
  });
});

document.getElementById("themeToggle").addEventListener("click", () => {
  document.body.classList.toggle("dark");
  document.body.classList.toggle("light");
});
//Here Events+DOM arde used to implement toggle functionality

function openModal(content) {
  modalBox.innerHTML = content;
  modal.classList.remove("hidden");
}
//This is used to remove the hidden and makes the modal visible
function closeModal() {
  modal.classList.add("hidden");
}
//This is used to re-add the hidden and make the modal disappear
modal.addEventListener("click", e => {
  if (e.target === modal) closeModal();
});
//Click outside to close modal
document.querySelectorAll(".action-btn").forEach(btn => {
  btn.addEventListener("click", () => {
//Action button event listeners


    if (btn.classList.contains("like") || btn.classList.contains("dislike")) {
      const countEl = btn.querySelector(".count");
      countEl.textContent = Number(countEl.textContent) + 1;

      openModal(
        btn.classList.contains("like")
          ? `<h3 class="feedback-like">Thank you for your feedback! 😊</h3>`
          : `<h3 class="feedback-dislike">We regret the inconvenience 😔</h3>`
      );

      setTimeout(closeModal, 2000);
    }

    if (btn.classList.contains("comment") || btn.classList.contains("query")) {
      openModal(`
        <h3>Submit Response</h3>
        <textarea rows="4" placeholder="Type here..."></textarea>
        <br /><br />
        <button onclick="closeModal()">Submit</button>
      `);
    }
  });
});

sortDropdown.addEventListener("change", () => {
  const items = Array.from(document.querySelectorAll(".accordion-item"));

  if (sortDropdown.value === "liked") {
    items.sort((a, b) => {
      const likesA = Number(a.querySelector(".like .count").textContent);
      const likesB = Number(b.querySelector(".like .count").textContent);
      return likesB - likesA; // DESC
    });
  }

  if (sortDropdown.value === "oldest") {
    items.sort((a, b) =>
      Number(a.dataset.index) - Number(b.dataset.index)
    );
  }

  if (sortDropdown.value === "newest") {
    items.sort((a, b) =>
      Number(b.dataset.index) - Number(a.dataset.index)
    );
  }

  // Re-append sorted items
  items.forEach(item => accordion.appendChild(item));
});
