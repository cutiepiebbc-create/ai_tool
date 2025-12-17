document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("searchInput");
    const searchBtn = document.getElementById("searchBtn");
    const resultsDiv = document.getElementById("results");

    searchBtn.addEventListener("click", () => {
        const query = searchInput.value.trim();
        if (!query) {
            alert("Please enter a product query.");
            return;
        }

        resultsDiv.innerHTML = "<p>Searching...</p>";

        fetch("/api/search", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ query })
        })
        .then(response => response.json())
        .then(data => {
            resultsDiv.innerHTML = "";

            if (data.error) {
                resultsDiv.innerHTML = `<p style="color:red;">Error: ${data.error}</p>`;
                return;
            }

            if (!data.results || data.results.length === 0) {
                resultsDiv.innerHTML = "<p>No results found.</p>";
                return;
            }

            data.results.forEach(product => {
                const productDiv = document.createElement("div");
                productDiv.className = "product";

                const img = document.createElement("img");
                img.src = product.image || "https://via.placeholder.com/100";
                productDiv.appendChild(img);

                const infoDiv = document.createElement("div");
                infoDiv.className = "product-info";

                const title = document.createElement("h3");
                title.textContent = product.title;
                infoDiv.appendChild(title);

                const price = document.createElement("p");
                price.textContent = `Price: ${product.price || "N/A"}`;
                infoDiv.appendChild(price);

                const link = document.createElement("a");
                link.href = product.link || "#";
                link.textContent = "View Product";
                link.target = "_blank";
                infoDiv.appendChild(link);

                productDiv.appendChild(infoDiv);
                resultsDiv.appendChild(productDiv);
            });
        })
        .catch(err => {
            resultsDiv.innerHTML = `<p style="color:red;">Request failed: ${err}</p>`;
        });
    });

    // Optional: allow pressing Enter to search
    searchInput.addEventListener("keyup", (e) => {
        if (e.key === "Enter") searchBtn.click();
    });
});
