const toast = document.querySelector("#toast");

function showToast(message, tone = "ok") {
  toast.textContent = message;
  toast.className = `toast show ${tone}`;
  window.setTimeout(() => {
    toast.className = "toast";
  }, 2400);
}

function markReviewed(card, data) {
  card.querySelector(".review-status").textContent = data.review.decision;
  card.querySelectorAll("button[data-action='review']").forEach((button) => {
    button.disabled = true;
  });
  const exportLink = card.querySelector(".export-link");
  exportLink.href = data.packet_url;
  exportLink.classList.remove("hidden");
}

document.querySelectorAll("button[data-action='review']").forEach((button) => {
  button.addEventListener("click", async () => {
    const card = button.closest(".claim-card");
    const claimId = card.dataset.claimId;
    const decision = button.dataset.decision;

    const response = await fetch(`/api/review/${claimId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ decision }),
    });
    const data = await response.json();

    if (!response.ok) {
      showToast(data.error || "Review failed.", "bad");
      return;
    }

    markReviewed(card, data);
    showToast(`${claimId} ${data.review.decision}.`);
  });
});

document.querySelector("#resetButton").addEventListener("click", async () => {
  const response = await fetch("/api/reset", {
    method: "POST",
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    showToast("Reset failed.", "bad");
    return;
  }
  window.location.reload();
});
