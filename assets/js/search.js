// Wiki search — reads pre-built search-index.json
(function () {
  const input = document.getElementById("search");
  const results = document.getElementById("search-results");
  if (!input || !results) return;

  let index = null;

  // Load index lazily on first focus
  input.addEventListener("focus", () => {
    if (index) return;
    fetch(BASE + "/search-index.json")
      .then(r => r.json())
      .then(data => { index = data; })
      .catch(() => {});
  }, { once: true });

  input.addEventListener("input", () => {
    const q = input.value.trim().toLowerCase();
    if (!q || q.length < 2 || !index) {
      results.classList.remove("open");
      return;
    }
    const hits = index
      .filter(p => p.title.toLowerCase().includes(q) || p.text.toLowerCase().includes(q))
      .slice(0, 7);

    if (!hits.length) { results.classList.remove("open"); return; }

    results.innerHTML = hits.map(p => {
      const idx = p.text.toLowerCase().indexOf(q);
      const start = Math.max(0, idx - 35);
      const snippet = p.text.slice(start, start + 120).replace(/\s+/g, " ");
      const hl = s => s.replace(new RegExp(q.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "gi"),
        m => `<mark>${m}</mark>`);
      return `<div class="sr-item" onclick="location.href='${p.url}'">
        <div class="sr-title">${hl(p.title)}</div>
        <div class="sr-snippet">${hl(snippet)}…</div>
      </div>`;
    }).join("");
    results.classList.add("open");
  });

  document.addEventListener("click", e => {
    if (!input.contains(e.target) && !results.contains(e.target)) {
      results.classList.remove("open");
    }
  });

  document.addEventListener("keydown", e => {
    if (e.key === "Escape") { results.classList.remove("open"); input.blur(); }
  });
})();
