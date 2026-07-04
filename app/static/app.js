const toast = document.querySelector("#toast");
const ledgerStatusPill = document.querySelector("#ledgerStatusPill");
const tamperButton = document.querySelector("#tamperButton");
const resetButtons = document.querySelectorAll("[data-action='reset']");
const demoModeEnabled = tamperButton?.dataset.demoMode === "true";

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

function formatValue(value, fallback = "No records yet") {
  return value === null || value === undefined || value === "" ? fallback : value;
}

function renderAudit(audit) {
  document.querySelector("[data-audit-field='entry-count']").textContent = audit.entry_count;
  document.querySelector("[data-audit-field='status']").textContent = audit.status;
  document.querySelector("[data-audit-field='latest-record-hash']").textContent = formatValue(
    audit.latest_record_hash,
  );

  const previousLink = audit.latest_previous_hash
    ? `stored ${audit.latest_previous_hash} -> expected ${audit.expected_previous_hash}`
    : "No records yet";
  document.querySelector("[data-audit-field='previous-hash-link']").textContent = previousLink;

  const statusBadge = document.querySelector("[data-audit-field='status-badge']");
  statusBadge.textContent = audit.status;
  statusBadge.className = `badge ${audit.valid ? "ok" : "bad"}`;

  ledgerStatusPill.textContent = `Ledger: ${audit.valid ? "valid" : "invalid"}`;
  ledgerStatusPill.className = `pill ${audit.valid ? "ok" : "bad"}`;

  const errors = document.querySelector("[data-audit-field='errors']");
  errors.replaceChildren();
  audit.errors.forEach((error) => {
    const row = document.createElement("div");
    row.textContent = error;
    errors.appendChild(row);
  });
  errors.classList.toggle("hidden", audit.errors.length === 0);

  if (tamperButton) {
    tamperButton.disabled = !demoModeEnabled || audit.entry_count === 0;
  }
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
    renderAudit(data.audit);
    showToast(`${claimId} ${data.review.decision}.`);
  });
});

if (tamperButton) {
  tamperButton.addEventListener("click", async () => {
    const response = await fetch("/api/audit/tamper", {
      method: "POST",
      headers: { Accept: "application/json" },
    });
    const data = await response.json();
    if (!response.ok) {
      if (data.audit) {
        renderAudit(data.audit);
      }
      showToast(data.error || "Tamper simulation failed.", "bad");
      return;
    }
    renderAudit(data.audit);
    showToast("Ledger tamper detected.", "bad");
  });
}

resetButtons.forEach((button) => {
  button.addEventListener("click", async () => {
    const response = await fetch("/api/reset", {
      method: "POST",
      headers: { Accept: "application/json" },
    });
    if (!response.ok) {
      const data = await response.json();
      showToast(data.error || "Reset failed.", "bad");
      return;
    }
    window.location.reload();
  });
});
