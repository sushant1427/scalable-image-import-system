const API_BASE = (location.hostname === "localhost" || location.hostname === "127.0.0.1")
  ? "http://localhost:8000"
  : (location.origin.replace(":8080", ":8000"));

async function refreshImages() {
  const tbody = document.getElementById("imagesBody");
  tbody.innerHTML = "";
  const res = await fetch(`${API_BASE}/images?limit=100`);
  const data = await res.json();

  for (const row of data) {
    const tr = document.createElement("tr");
    const storageLink = row.storage_path ? `<a href="${row.storage_path}" target="_blank">open</a>` : "";
    tr.innerHTML = `
      <td>${row.id}</td>
      <td>${row.name}</td>
      <td>${row.mime_type || ""}</td>
      <td>${row.size || ""}</td>
      <td>${storageLink}</td>
      <td>${row.import_id || ""}</td>
    `;
    tbody.appendChild(tr);
  }
}

document.getElementById("refreshBtn").addEventListener("click", refreshImages);

document.getElementById("importForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const folderUrl = document.getElementById("folderUrl").value.trim();
  const out = document.getElementById("importResult");
  out.textContent = "Submitting...";

  const res = await fetch(`${API_BASE}/import/google-drive`, {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({ folder_url: folderUrl })
  });

  const data = await res.json();
  out.textContent = JSON.stringify(data, null, 2);
  await refreshImages();
});

// auto refresh
refreshImages();
