document.addEventListener("DOMContentLoaded", () => {
  const searchInput = document.getElementById("searchInput");
  const searchBtn = document.getElementById("searchBtn");
  const resultsDiv = document.getElementById("results");
  const statusDiv = document.getElementById("status");

  async function search() {
    const query = searchInput.value.trim();
    resultsDiv.innerHTML = "";
    statusDiv.textContent = "";

    if (!query) {
      statusDiv.textContent = "Please enter a search query.";
      return;
    }

    statusDiv.textContent = "Searching…";

    try {
      const res = await fetch("/api/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query })
      });

      const data = await res.json();
      statusDiv.textContent = "";

      if (!data.results || data.results.length === 0) {
        statusDiv.textContent = "No results found.";
        return;
      }

      data.results.forEach(product => {
        const card = document.createElement("div");
        card.className = "product-card";

        card.innerHTML = `
          <img src="${product.image || "https://via.placeholder.com/200"}" />
          <a class="product-title" href="${product.link}" target="_blank">
            ${product.title}
          </a>
          <div class="product-price">${product.price || "N/A"}</div>
          <a class="view-btn" href="${product.link}" target="_blank">
            View on eBay
          </a>
        `;

        resultsDiv.appendChild(card);
      });

    } catch (err) {
      statusDiv.textContent = "Search failed. Try again.";
      console.error(err);
    }
  }

  searchBtn.addEventListener("click", search);

  searchInput.addEventListener("keydown", e => {
    if (e.key === "Enter") search();
  });
});
