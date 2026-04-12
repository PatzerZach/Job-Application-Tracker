/* ============================================================
   TRACKR — app.js
   Particles · 3D Tilt · Scroll Reveal · Counters · Micro-FX
   ============================================================ */

/* ── Theme ───────────────────────────────────────────────────── */
const THEME_KEY = "appstrackr-theme";

function getTheme() {
  return (
    localStorage.getItem(THEME_KEY) ||
    (window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light")
  );
}

function applyTheme(t) {
  document.documentElement.setAttribute("data-theme", t);
  localStorage.setItem(THEME_KEY, t);
}

function toggleTheme() {
  applyTheme(getTheme() === "dark" ? "light" : "dark");
}

// Immediate apply (no flash)
(function () {
  applyTheme(getTheme());
})();

/* ── DOM Ready ───────────────────────────────────────────────── */
document.addEventListener("DOMContentLoaded", () => {
  document
    .querySelectorAll(".theme-toggle")
    .forEach((btn) => btn.addEventListener("click", toggleTheme));

  initParticles();
  initNavScroll();
  initScrollReveal();
  initFeatureCardGlow();
  init3DTilt();
  initCounters();
  initMobileSidebar();
  initFileUpload();
  initDocumentComposers();
  initDocumentPreviewModal();
  initConfirmDelete();
  initTableSearch();
  initAlertDismiss();
  initFormValidation();
  initStatusBadge();
  initAutoResize();
  initCustomDatePickers();
  initNumberSteppers();
  initLocationPickers();
  initHeroParallax();
  initTextScramble();

  // Auto-dismiss flash alerts
  document.querySelectorAll(".alert[data-auto-dismiss]").forEach((el) => {
    setTimeout(() => dismissAlert(el), 4500);
  });
});

/* ── Particle System ─────────────────────────────────────────── */
function initParticles() {
  const canvas = document.getElementById("particles-canvas");
  if (!canvas) return;

  const ctx = canvas.getContext("2d");
  let W,
    H,
    particles = [],
    mouse = { x: -9999, y: -9999 };

  const isDark = () =>
    document.documentElement.getAttribute("data-theme") !== "light";

  function resize() {
    W = canvas.width = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }

  resize();
  window.addEventListener("resize", resize, { passive: true });

  window.addEventListener(
    "mousemove",
    (e) => {
      mouse.x = e.clientX;
      mouse.y = e.clientY;
    },
    { passive: true },
  );

  const PARTICLE_COUNT = 55;

  class Particle {
    constructor() {
      this.reset(true);
    }

    reset(initial = false) {
      this.x = Math.random() * W;
      this.y = initial ? Math.random() * H : H + 10;
      this.size = Math.random() * 1.6 + 0.4;
      this.speedX = (Math.random() - 0.5) * 0.4;
      this.speedY = -(Math.random() * 0.5 + 0.2);
      this.opacity = 0;
      this.maxOpacity = Math.random() * 0.4 + 0.1;
      this.life = 0;
      this.maxLife = Math.random() * 400 + 200;
      this.hue =
        Math.random() > 0.7
          ? 200 + Math.random() * 60
          : 40 + Math.random() * 15;
      this.glow = Math.random() > 0.85;
    }

    update() {
      this.x += this.speedX;
      this.y += this.speedY;
      this.life++;

      // Mouse repel
      const dx = this.x - mouse.x;
      const dy = this.y - mouse.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < 120) {
        const force = (120 - dist) / 120;
        this.x += (dx / dist) * force * 1.2;
        this.y += (dy / dist) * force * 1.2;
      }

      // Fade in / out
      const halfLife = this.maxLife / 2;
      if (this.life < 60) {
        this.opacity = (this.life / 60) * this.maxOpacity;
      } else if (this.life > this.maxLife - 80) {
        this.opacity = ((this.maxLife - this.life) / 80) * this.maxOpacity;
      } else {
        this.opacity = this.maxOpacity;
      }

      if (this.life > this.maxLife || this.y < -20) this.reset();
    }

    draw() {
      const dark = isDark();
      ctx.save();
      ctx.globalAlpha = this.opacity;

      if (this.glow) {
        ctx.shadowColor = `hsl(${this.hue}, 80%, 65%)`;
        ctx.shadowBlur = 10;
      }

      ctx.beginPath();
      ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
      ctx.fillStyle = `hsl(${this.hue}, ${dark ? 70 : 50}%, ${dark ? 70 : 45}%)`;
      ctx.fill();
      ctx.restore();
    }
  }

  for (let i = 0; i < PARTICLE_COUNT; i++) particles.push(new Particle());

  // Draw connecting lines between nearby particles
  function drawConnections() {
    const MAX_DIST = 100;
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const p1 = particles[i],
          p2 = particles[j];
        const dx = p1.x - p2.x;
        const dy = p1.y - p2.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < MAX_DIST) {
          const alpha = (1 - dist / MAX_DIST) * 0.06;
          ctx.save();
          ctx.globalAlpha = alpha;
          ctx.strokeStyle = isDark()
            ? "rgba(240,200,74,0.8)"
            : "rgba(184,134,11,0.8)";
          ctx.lineWidth = 0.5;
          ctx.beginPath();
          ctx.moveTo(p1.x, p1.y);
          ctx.lineTo(p2.x, p2.y);
          ctx.stroke();
          ctx.restore();
        }
      }
    }
  }

  let rafId;
  function animate() {
    ctx.clearRect(0, 0, W, H);
    drawConnections();
    particles.forEach((p) => {
      p.update();
      p.draw();
    });
    rafId = requestAnimationFrame(animate);
  }

  animate();

  // Pause when not visible
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) cancelAnimationFrame(rafId);
    else animate();
  });
}

/* ── Navbar Scroll ───────────────────────────────────────────── */
function initNavScroll() {
  const nav = document.querySelector(".pub-nav");
  if (!nav) return;
  const handler = () => nav.classList.toggle("scrolled", window.scrollY > 30);
  window.addEventListener("scroll", handler, { passive: true });
  handler();
}

/* ── Scroll Reveal ───────────────────────────────────────────── */
function initScrollReveal() {
  const els = document.querySelectorAll("[data-reveal]");
  if (!els.length) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("revealed");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.12, rootMargin: "0px 0px -40px 0px" },
  );

  els.forEach((el) => observer.observe(el));
}

/* ── Feature Card Mouse-tracking Glow ───────────────────────── */
function initFeatureCardGlow() {
  document.querySelectorAll(".feature-card").forEach((card) => {
    const glow = card.querySelector(".feature-card-glow");
    if (!glow) {
      // Create it if not present
      const g = document.createElement("div");
      g.className = "feature-card-glow";
      card.prepend(g);
    }

    card.addEventListener("mousemove", (e) => {
      const rect = card.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width) * 100;
      const y = ((e.clientY - rect.top) / rect.height) * 100;
      card.style.setProperty("--mx", `${x}%`);
      card.style.setProperty("--my", `${y}%`);
    });
  });
}

/* ── 3D Tilt Effect ──────────────────────────────────────────── */
function init3DTilt() {
  if (window.matchMedia("(hover: none)").matches) return;
  document
    .querySelectorAll(
      ".tilt-card, .feature-card, .step-card, .auth-card, .hero-dashboard-inner",
    )
    .forEach((el) => {
      el.addEventListener("mousemove", (e) => {
        const rect = el.getBoundingClientRect();
        const cx = rect.left + rect.width / 2;
        const cy = rect.top + rect.height / 2;
        const dx = (e.clientX - cx) / (rect.width / 2);
        const dy = (e.clientY - cy) / (rect.height / 2);

        const maxTilt = el.dataset.tilt ? parseFloat(el.dataset.tilt) : 8;
        const rotY = dx * maxTilt;
        const rotX = -dy * maxTilt;

        el.style.transform = `perspective(1000px) rotateX(${rotX}deg) rotateY(${rotY}deg) translateZ(4px)`;
      });

      el.addEventListener("mouseleave", () => {
        el.style.transition = "transform 0.6s cubic-bezier(0.34,1.56,0.64,1)";
        el.style.transform = "";
        setTimeout(() => {
          el.style.transition = "";
        }, 600);
      });

      el.addEventListener("mouseenter", () => {
        el.style.transition = "transform 0.1s ease";
      });
    });
}

/* ── Animated Counters ───────────────────────────────────────── */
function initCounters() {
  const counters = document.querySelectorAll("[data-count]");
  if (!counters.length) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        const el = entry.target;
        const target = parseInt(el.dataset.count, 10);
        const duration = 1200;
        const start = performance.now();

        function update(now) {
          const progress = Math.min((now - start) / duration, 1);
          const eased = 1 - Math.pow(1 - progress, 3);
          el.textContent = Math.round(eased * target).toLocaleString();
          if (progress < 1) requestAnimationFrame(update);
          else
            el.textContent =
              target.toLocaleString() + (el.dataset.suffix || "");
        }

        requestAnimationFrame(update);
        observer.unobserve(el);
      });
    },
    { threshold: 0.5 },
  );

  counters.forEach((c) => observer.observe(c));
}

/* ── Mobile Sidebar ──────────────────────────────────────────── */
function initMobileSidebar() {
  const toggle = document.querySelector(".mobile-menu-toggle");
  const sidebar = document.querySelector(".sidebar");
  const overlay = document.querySelector(".sidebar-overlay");
  if (!toggle || !sidebar) return;

  const open = () => {
    sidebar.classList.add("open");
    overlay?.classList.add("active");
    document.body.style.overflow = "hidden";
    toggle.setAttribute("aria-expanded", "true");
  };
  const close = () => {
    sidebar.classList.remove("open");
    overlay?.classList.remove("active");
    document.body.style.overflow = "";
    toggle.setAttribute("aria-expanded", "false");
  };

  toggle.addEventListener("click", () =>
    sidebar.classList.contains("open") ? close() : open(),
  );
  overlay?.addEventListener("click", close);
  sidebar.querySelectorAll(".sidebar-item").forEach((item) => {
    item.addEventListener("click", () => {
      if (window.innerWidth <= 768) close();
    });
  });
}

/* ── File Upload ─────────────────────────────────────────────── */
function initFileUpload() {
  document.querySelectorAll(".file-upload-area").forEach((area) => {
    const input = area.querySelector('input[type="file"]');
    if (!input) return;

    const form = area.closest("form");
    const group = area.closest(".form-group") || area.parentElement;
    const selectedDisplay = group?.querySelector(".file-selected");
    const nameEl = group?.querySelector(".file-selected-name");
    const autofillInput = form?.querySelector("[data-autofill-from-file]");

    function inferNameFromFile(fileName) {
      if (!autofillInput || !fileName || autofillInput.value.trim()) return;
      autofillInput.value = fileName.replace(/\.[^.]+$/, "");
    }

    ["dragenter", "dragover"].forEach((evt) =>
      area.addEventListener(evt, (e) => {
        e.preventDefault();
        area.classList.add("dragging");
      }),
    );
    ["dragleave", "drop"].forEach((evt) =>
      area.addEventListener(evt, (e) => {
        e.preventDefault();
        area.classList.remove("dragging");
      }),
    );

    area.addEventListener("drop", (e) => {
      const file = e.dataTransfer?.files?.[0];
      if (file) {
        if (e.dataTransfer?.files?.length) {
          input.files = e.dataTransfer.files;
          input.dispatchEvent(new Event("change", { bubbles: true }));
        }
        inferNameFromFile(file.name);
        showFileSelected(file.name, nameEl, selectedDisplay);
      }
    });

    input.addEventListener("change", () => {
      if (input.files?.[0]) {
        inferNameFromFile(input.files[0].name);
        showFileSelected(input.files[0].name, nameEl, selectedDisplay);
      }
    });
  });
}

function showFileSelected(name, nameEl, wrapEl) {
  if (nameEl) nameEl.textContent = name;
  if (wrapEl) wrapEl.style.display = "flex";
}

function initDocumentComposers() {
  document.querySelectorAll("[data-document-picker]").forEach((picker) => {
    const modeInputs = picker.querySelectorAll("[data-document-mode]");
    const existingSelect = picker.querySelector("[data-document-existing]");
    const fileInput = picker.querySelector("[data-document-file]");
    const nameInput = picker.querySelector("[data-document-name]");
    const errorEls = picker.querySelectorAll("[data-document-error]");
    const isRequired = picker.dataset.required === "true";

    function getMode() {
      const selected = picker.querySelector("[data-document-mode]:checked");
      return selected ? selected.value : "existing";
    }

    function validateDocumentPicker() {
      const mode = getMode();
      let valid = true;

      if (isRequired) {
        valid =
          mode === "upload"
            ? Boolean(fileInput?.files?.length)
            : Boolean(existingSelect?.value);
      }

      picker.classList.toggle("is-invalid", !valid);
      errorEls.forEach((errorEl) => {
        errorEl.style.display = valid ? "none" : "block";
      });
      if (existingSelect)
        existingSelect.classList.toggle(
          "is-invalid",
          !valid && mode === "existing",
        );
      if (fileInput)
        fileInput.classList.toggle("is-invalid", !valid && mode === "upload");
      return valid;
    }

    function syncPanels() {
      const mode = getMode();
      picker.querySelectorAll("[data-document-panel]").forEach((panel) => {
        panel.classList.toggle(
          "is-active",
          panel.dataset.documentPanel === mode,
        );
      });
      picker.dataset.mode = mode;
      validateDocumentPicker();
    }

    function inferNameFromFile() {
      if (
        !fileInput ||
        !nameInput ||
        !fileInput.files?.length ||
        nameInput.value.trim()
      )
        return;
      nameInput.value = fileInput.files[0].name.replace(/\.[^.]+$/, "");
    }

    modeInputs.forEach((input) => input.addEventListener("change", syncPanels));
    existingSelect?.addEventListener("change", validateDocumentPicker);
    fileInput?.addEventListener("change", () => {
      inferNameFromFile();
      validateDocumentPicker();
    });

    syncPanels();

    const form = picker.closest("form");
    if (!form) return;

    form.addEventListener("submit", (event) => {
      if (!validateDocumentPicker()) {
        event.preventDefault();
        picker.scrollIntoView({ behavior: "smooth", block: "center" });
      }
    });
  });
}

/* ── Confirm Delete Modal ────────────────────────────────────── */
function initConfirmDelete() {
  document.querySelectorAll("[data-confirm]").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      const message =
        btn.dataset.confirm || "Are you sure? This cannot be undone.";
      const form = btn.closest("form");
      showConfirmModal(message, () => {
        if (form) form.submit();
      });
    });
  });
}

function initDocumentPreviewModal() {
  const modal = document.getElementById("document-preview-modal");
  if (!modal) return;

  const closeBtn = document.getElementById("document-preview-close");
  const openLink = document.getElementById("document-preview-open");
  const downloadLink = document.getElementById("document-preview-download");
  const titleEl = document.getElementById("document-preview-title");
  const subtitleEl = document.getElementById("document-preview-filename");
  const typeEl = document.getElementById("document-preview-type");
  const extensionEl = document.getElementById("document-preview-extension");
  const loadingEl = document.getElementById("document-preview-loading");
  const frameShell = document.getElementById("document-preview-frame-shell");
  const frame = document.getElementById("document-preview-frame");
  const pdfShell = document.getElementById("document-preview-pdf-shell");
  const pdfStage = document.getElementById("document-preview-pdf-stage");
  const docxShell = document.getElementById("document-preview-docx-shell");
  const docxStage = document.getElementById("document-preview-docx-stage");

  if (
    !closeBtn ||
    !openLink ||
    !downloadLink ||
    !titleEl ||
    !subtitleEl ||
    !typeEl ||
    !extensionEl ||
    !loadingEl ||
    !frameShell ||
    !frame ||
    !pdfShell ||
    !pdfStage ||
    !docxShell ||
    !docxStage
  ) {
    return;
  }

  let frameLoadHandler = null;
  let previewToken = 0;

  if (window.pdfjsLib) {
    window.pdfjsLib.GlobalWorkerOptions.workerSrc =
      "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";
  }

  function hideAllPreviewPanels() {
    frameShell.hidden = true;
    pdfShell.hidden = true;
    docxShell.hidden = true;
  }

  function resetViewer() {
    loadingEl.hidden = false;
    hideAllPreviewPanels();
    openLink.href = "#";
    downloadLink.href = "#";

    if (frameLoadHandler) {
      frame.removeEventListener("load", frameLoadHandler);
      frameLoadHandler = null;
    }

    frame.removeAttribute("src");
    pdfStage.innerHTML = "";
    docxStage.innerHTML = "";
  }

  function showPreviewError(message) {
    loadingEl.hidden = true;
    hideAllPreviewPanels();
    showToast(message || "Preview unavailable for this file.", "error", 4500);
  }

  function showIframePreview(src, currentToken, fallbackMessage) {
    if (!src) {
      showPreviewError(fallbackMessage);
      return;
    }

    let didLoad = false;
    const timeoutId = window.setTimeout(() => {
      if (
        didLoad ||
        currentToken !== previewToken ||
        !modal.classList.contains("active")
      )
        return;
      showPreviewError(fallbackMessage);
    }, 5000);

    frameLoadHandler = () => {
      didLoad = true;
      window.clearTimeout(timeoutId);
      if (currentToken !== previewToken || !modal.classList.contains("active"))
        return;
      loadingEl.hidden = true;
      hideAllPreviewPanels();
      frameShell.hidden = false;
    };

    frame.addEventListener("load", frameLoadHandler, { once: true });
    frame.src = src;
  }

  async function renderPdfPreview(contentUrl, currentToken, fallbackMessage) {
    if (
      !(window.pdfjsLib && typeof window.pdfjsLib.getDocument === "function")
    ) {
      throw new Error("PDF renderer unavailable");
    }

    const response = await fetch(contentUrl, {
      headers: {
        Accept: "application/pdf",
        "X-Requested-With": "fetch",
      },
    });

    if (!response.ok) {
      throw new Error("PDF content unavailable");
    }

    const buffer = await response.arrayBuffer();
    if (currentToken !== previewToken || !modal.classList.contains("active"))
      return;

    const pdfDocument = await window.pdfjsLib.getDocument({
      data: new Uint8Array(buffer),
    }).promise;
    if (currentToken !== previewToken || !modal.classList.contains("active"))
      return;

    pdfStage.innerHTML = "";
    hideAllPreviewPanels();
    pdfShell.hidden = false;
    await new Promise((resolve) => requestAnimationFrame(resolve));

    const availableWidth = Math.max(pdfShell.clientWidth - 72, 420);
    const targetPageWidth = Math.min(availableWidth, 1040);
    const pixelRatio = window.devicePixelRatio || 1;

    for (
      let pageNumber = 1;
      pageNumber <= pdfDocument.numPages;
      pageNumber += 1
    ) {
      const page = await pdfDocument.getPage(pageNumber);
      if (currentToken !== previewToken || !modal.classList.contains("active"))
        return;

      const baseViewport = page.getViewport({ scale: 1 });
      const scale = targetPageWidth / baseViewport.width;
      const viewport = page.getViewport({ scale });

      const pageWrap = document.createElement("section");
      pageWrap.className = "document-preview-pdf-page";

      const pageMeta = document.createElement("div");
      pageMeta.className = "document-preview-pdf-meta";
      pageMeta.textContent = `Page ${pageNumber}`;

      const canvas = document.createElement("canvas");
      canvas.className = "document-preview-pdf-canvas";
      canvas.width = Math.floor(viewport.width * pixelRatio);
      canvas.height = Math.floor(viewport.height * pixelRatio);
      canvas.style.width = `${viewport.width}px`;
      canvas.style.height = `${viewport.height}px`;

      pageWrap.appendChild(pageMeta);
      pageWrap.appendChild(canvas);
      pdfStage.appendChild(pageWrap);

      const context = canvas.getContext("2d", { alpha: false });
      await page.render({
        canvasContext: context,
        viewport,
        transform:
          pixelRatio !== 1 ? [pixelRatio, 0, 0, pixelRatio, 0, 0] : null,
      }).promise;

      if (
        pageNumber === 1 &&
        currentToken === previewToken &&
        modal.classList.contains("active")
      ) {
        loadingEl.hidden = true;
        hideAllPreviewPanels();
        pdfShell.hidden = false;
      }
    }

    if (currentToken === previewToken && modal.classList.contains("active")) {
      loadingEl.hidden = true;
      hideAllPreviewPanels();
      pdfShell.hidden = false;
    }
  }

  async function renderDocxPreview(contentUrl, currentToken, fallbackMessage) {
    if (!(window.docx && typeof window.docx.renderAsync === "function")) {
      throw new Error("DOCX renderer unavailable");
    }

    const response = await fetch(contentUrl, {
      headers: {
        Accept: "application/octet-stream",
        "X-Requested-With": "fetch",
      },
    });

    if (!response.ok) {
      throw new Error("DOCX content unavailable");
    }

    const buffer = await response.arrayBuffer();
    if (currentToken !== previewToken || !modal.classList.contains("active"))
      return;

    docxStage.innerHTML = "";

    await window.docx.renderAsync(buffer, docxStage, docxStage, {
      inWrapper: true,
      ignoreWidth: false,
      ignoreHeight: true,
      breakPages: true,
      useBase64URL: true,
      renderHeaders: true,
      renderFooters: true,
    });

    if (currentToken !== previewToken || !modal.classList.contains("active"))
      return;

    loadingEl.hidden = true;
    hideAllPreviewPanels();
    docxShell.hidden = false;
  }

  function closeModal() {
    previewToken += 1;
    modal.classList.remove("active");
    document.body.style.overflow = "";
    resetViewer();
  }

  function openModalFromButton(button) {
    typeEl.textContent = button.dataset.documentType || "Document";
    extensionEl.textContent = button.dataset.documentExtension || "FILE";
    titleEl.textContent = button.dataset.documentName || "Preview";
    subtitleEl.textContent = button.dataset.documentFilename || "Stored file";
    resetViewer();
    modal.classList.add("active");
    document.body.style.overflow = "hidden";
  }

  async function loadPreview(button) {
    const currentToken = ++previewToken;
    const endpoint = button.dataset.previewEndpoint;
    if (!endpoint) {
      showPreviewError(
        "Preview details are unavailable for this document right now.",
      );
      return;
    }

    try {
      const response = await fetch(endpoint, {
        headers: {
          Accept: "application/json",
          "X-Requested-With": "fetch",
        },
      });

      if (!response.ok) throw new Error("Preview unavailable");

      const payload = await response.json();
      if (currentToken !== previewToken || !modal.classList.contains("active"))
        return;
      const openUrl =
        payload.document_open_url ||
        payload.document_external_url ||
        payload.viewer_src ||
        "#";
      const downloadUrl = payload.document_download_url || openUrl;
      const fallbackMessage =
        payload.viewer_note ||
        "We could not load the inline preview right now. Try opening the raw file or downloading it.";

      openLink.href = openUrl;
      downloadLink.href = downloadUrl;

      if (payload.viewer_mode === "pdf" && payload.content_url) {
        await renderPdfPreview(
          payload.content_url,
          currentToken,
          fallbackMessage,
        );
        return;
      }

      if (payload.viewer_mode === "office") {
        showIframePreview(payload.viewer_src, currentToken, fallbackMessage);
        return;
      }

      if (payload.viewer_mode === "docx" && payload.content_url) {
        await renderDocxPreview(
          payload.content_url,
          currentToken,
          fallbackMessage,
        );
        return;
      }

      showPreviewError(fallbackMessage);
    } catch (error) {
      console.error("Document preview failed", error);
      if (currentToken !== previewToken || !modal.classList.contains("active"))
        return;
      showPreviewError(
        "We could not load the inline preview right now. Try opening the raw file or downloading it.",
      );
    }
  }

  document.querySelectorAll("[data-document-preview]").forEach((button) => {
    button.addEventListener("click", (event) => {
      event.preventDefault();
      openModalFromButton(button);
      loadPreview(button);
    });
  });

  closeBtn.addEventListener("click", closeModal);
  modal.addEventListener("click", (event) => {
    if (event.target === modal) closeModal();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && modal.classList.contains("active"))
      closeModal();
  });
}

function showConfirmModal(message, onConfirm) {
  const overlay = document.getElementById("confirm-modal");
  const msgEl = document.getElementById("confirm-message");
  const confirmBtn = document.getElementById("confirm-yes");
  const cancelBtn = document.getElementById("confirm-no");
  if (!overlay) return onConfirm();

  if (msgEl) msgEl.textContent = message;
  overlay.classList.add("active");
  confirmBtn.focus();

  function cleanup() {
    overlay.classList.remove("active");
    confirmBtn.removeEventListener("click", yes);
    cancelBtn.removeEventListener("click", no);
  }
  function yes() {
    cleanup();
    onConfirm();
  }
  function no() {
    cleanup();
  }

  confirmBtn.addEventListener("click", yes);
  cancelBtn.addEventListener("click", no);
  overlay.addEventListener(
    "click",
    (e) => {
      if (e.target === overlay) no();
    },
    { once: true },
  );
}

/* ── Table Search ────────────────────────────────────────────── */
function initTableSearch() {
  const input = document.getElementById("table-search");
  if (!input) return;
  const table = document.querySelector("[data-searchable]");
  if (!table) return;

  input.addEventListener("input", () => {
    const q = input.value.toLowerCase();
    let visible = 0;
    table.querySelectorAll("tbody tr:not(.table-empty-row)").forEach((row) => {
      const haystack = (
        row.dataset.searchText || row.textContent
      ).toLowerCase();
      const match = !q || haystack.includes(q);
      row.style.display = match ? "" : "none";
      if (match) visible++;
    });
    const emptyRow = table.querySelector(".table-empty-row");
    if (emptyRow) emptyRow.style.display = visible === 0 ? "" : "none";
  });
}

/* ── Alert Dismiss ───────────────────────────────────────────── */
function initAlertDismiss() {
  document
    .querySelectorAll(".alert-close")
    .forEach((btn) =>
      btn.addEventListener("click", () => dismissAlert(btn.closest(".alert"))),
    );
}

function dismissAlert(el) {
  if (!el) return;
  el.style.transition = "opacity 0.28s ease, transform 0.28s ease";
  el.style.opacity = "0";
  el.style.transform = "translateY(-10px)";
  setTimeout(() => el.remove(), 280);
}

/* Date Picker */
function initCustomDatePickers() {
  const pickers = document.querySelectorAll("[data-date-picker]");
  if (!pickers.length) return;

  const monthNames = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
  ];
  const weekdayLabels = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"];
  let openPicker = null;

  function parseDate(value) {
    if (!value) return null;
    const [year, month, day] = value.split("-").map(Number);
    if (!year || !month || !day) return null;
    return new Date(year, month - 1, day);
  }

  function toIso(date) {
    const year = date.getFullYear();
    const month = `${date.getMonth() + 1}`.padStart(2, "0");
    const day = `${date.getDate()}`.padStart(2, "0");
    return `${year}-${month}-${day}`;
  }

  function formatHuman(date) {
    return `${monthNames[date.getMonth()]} ${date.getDate()}, ${date.getFullYear()}`;
  }

  function closePicker(picker) {
    if (!picker) return;
    const popover = picker.querySelector("[data-date-popover]");
    const trigger = picker.querySelector("[data-date-trigger]");
    if (!popover || !trigger) return;
    picker.classList.remove("open");
    popover.hidden = true;
    trigger.setAttribute("aria-expanded", "false");
    if (openPicker === picker) openPicker = null;
  }

  function updateLabel(picker) {
    const valueInput = picker.querySelector("[data-date-value]");
    const label = picker.querySelector("[data-date-label]");
    if (!valueInput || !label) return;
    const selected = parseDate(valueInput.value);
    label.textContent = selected ? formatHuman(selected) : "Select a date";
    label.classList.toggle("is-empty", !selected);
  }

  function renderPicker(picker) {
    const popover = picker.querySelector("[data-date-popover]");
    const valueInput = picker.querySelector("[data-date-value]");
    if (!popover || !valueInput) return;

    const selectedDate = parseDate(valueInput.value);
    const viewDate = picker._viewDate || selectedDate || new Date();
    const monthStart = new Date(viewDate.getFullYear(), viewDate.getMonth(), 1);
    const gridStart = new Date(monthStart);
    gridStart.setDate(1 - monthStart.getDay());
    const todayIso = toIso(new Date());

    const days = [];
    for (let i = 0; i < 42; i += 1) {
      const day = new Date(gridStart);
      day.setDate(gridStart.getDate() + i);
      const iso = toIso(day);
      days.push(`
        <button type="button"
          class="custom-date-day${day.getMonth() !== viewDate.getMonth() ? " is-outside" : ""}${iso === todayIso ? " is-today" : ""}${valueInput.value === iso ? " is-selected" : ""}"
          data-date-day="${iso}"
          aria-label="${formatHuman(day)}">
          ${day.getDate()}
        </button>
      `);
    }

    popover.innerHTML = `
      <div class="custom-date-header">
        <button type="button" class="custom-date-nav" data-date-nav="-1" aria-label="Previous month">
          <svg viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M7.5 2L3.5 6l4 4"/></svg>
        </button>
        <div class="custom-date-month">${monthNames[viewDate.getMonth()]} ${viewDate.getFullYear()}</div>
        <button type="button" class="custom-date-nav" data-date-nav="1" aria-label="Next month">
          <svg viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4.5 2l4 4-4 4"/></svg>
        </button>
      </div>
      <div class="custom-date-weekdays">
        ${weekdayLabels.map((label) => `<div class="custom-date-weekday">${label}</div>`).join("")}
      </div>
      <div class="custom-date-grid">${days.join("")}</div>
      <div class="custom-date-footer">
        <div class="custom-date-footer-note">${selectedDate ? `Locked on ${formatHuman(selectedDate)}` : "Choose a day to lock it in"}</div>
        <div class="custom-date-footer-actions">
          <button type="button" class="custom-date-footer-btn" data-date-action="today">Today</button>
          <button type="button" class="custom-date-footer-btn" data-date-action="clear">Clear</button>
        </div>
      </div>
    `;

    popover.querySelectorAll("[data-date-nav]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const next = new Date(viewDate);
        next.setMonth(next.getMonth() + Number(btn.dataset.dateNav));
        picker._viewDate = next;
        renderPicker(picker);
      });
    });

    popover.querySelectorAll("[data-date-day]").forEach((btn) => {
      btn.addEventListener("click", () => {
        valueInput.value = btn.dataset.dateDay;
        picker._viewDate = parseDate(btn.dataset.dateDay);
        updateLabel(picker);
        renderPicker(picker);
        closePicker(picker);
      });
    });

    popover
      .querySelector('[data-date-action="today"]')
      ?.addEventListener("click", () => {
        const today = new Date();
        valueInput.value = toIso(today);
        picker._viewDate = today;
        updateLabel(picker);
        renderPicker(picker);
        closePicker(picker);
      });

    popover
      .querySelector('[data-date-action="clear"]')
      ?.addEventListener("click", () => {
        valueInput.value = "";
        picker._viewDate = new Date();
        updateLabel(picker);
        renderPicker(picker);
      });
  }

  pickers.forEach((picker) => {
    const trigger = picker.querySelector("[data-date-trigger]");
    if (!trigger) return;
    updateLabel(picker);
    renderPicker(picker);

    picker.addEventListener("click", (event) => {
      event.stopPropagation();
    });

    trigger.addEventListener("click", () => {
      if (openPicker && openPicker !== picker) closePicker(openPicker);
      const popover = picker.querySelector("[data-date-popover]");
      const isOpen = picker.classList.contains("open");
      if (!popover) return;
      if (isOpen) {
        closePicker(picker);
      } else {
        picker.classList.add("open");
        popover.hidden = false;
        trigger.setAttribute("aria-expanded", "true");
        openPicker = picker;
        renderPicker(picker);
      }
    });
  });

  document.addEventListener("click", (event) => {
    if (openPicker && !openPicker.contains(event.target)) {
      closePicker(openPicker);
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && openPicker) closePicker(openPicker);
  });
}

/* Number Steppers */
function initNumberSteppers() {
  document.querySelectorAll("[data-number-stepper]").forEach((wrap) => {
    const input = wrap.querySelector('input[type="number"]');
    if (!input) return;
    wrap.querySelectorAll("[data-step-action]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const step = Number(input.step || 1);
        const current = input.value === "" ? 0 : Number(input.value);
        const direction = btn.dataset.stepAction === "up" ? 1 : -1;
        const min =
          input.min === "" ? Number.NEGATIVE_INFINITY : Number(input.min);
        const next = Math.max(min, current + step * direction);
        input.value = Number.isFinite(next)
          ? next.toFixed(step < 1 ? 2 : 0).replace(/\.00$/, "")
          : "";
        input.dispatchEvent(new Event("input", { bubbles: true }));
      });
    });
  });
}

/* Location Pickers */
function initLocationPickers() {
  const pickers = document.querySelectorAll("[data-location-picker]");
  if (!pickers.length) return;

  const defaultView = { lat: 39.8283, lng: -98.5795, zoom: 4 };
  const searchCache = new Map();

  function compactLocationLabel(result) {
    return (
      [result.city, result.state, result.country].filter(Boolean).join(", ") ||
      result.label ||
      result.full_label ||
      ""
    );
  }

  function setLocationFields(picker, result) {
    const form = picker.closest("form");
    const city = form?.querySelector('input[name="job_city"]');
    const state = form?.querySelector('input[name="job_state"]');
    const country = form?.querySelector('input[name="job_country"]');
    if (city) city.value = result.city || "";
    if (state) state.value = result.state || "";
    if (country) country.value = result.country || "";
  }

  function renderResults(container, results, onSelect) {
    if (!container) return;
    if (!results.length) {
      container.hidden = true;
      container.innerHTML = "";
      return;
    }
    container.innerHTML = results
      .map(
        (result, index) => `
      <button type="button" class="location-search-result" data-location-result-index="${index}">
        <span class="location-search-result-title">${compactLocationLabel(result) || "Unknown place"}</span>
        <span class="location-search-result-meta">${[result.city, result.state, result.country].filter(Boolean).join(" • ")}</span>
      </button>
    `,
      )
      .join("");
    container.hidden = false;
    container
      .querySelectorAll("[data-location-result-index]")
      .forEach((btn) => {
        btn.addEventListener("click", () =>
          onSelect(results[Number(btn.dataset.locationResultIndex)]),
        );
      });
  }

  pickers.forEach((picker) => {
    const searchInput = picker.querySelector("[data-location-search]");
    const resultsWrap = picker.querySelector("[data-location-results]");
    const mapNode = picker.querySelector("[data-location-map]");
    const resetBtn = picker.querySelector("[data-location-reset]");
    const enabled = mapNode?.dataset.geoapifyEnabled === "true";
    let marker = null;
    let map = null;
    let debounceId = null;

    function applySelection(result, focusMap = true) {
      setLocationFields(picker, result);
      if (searchInput) searchInput.value = compactLocationLabel(result);
      renderResults(resultsWrap, [], () => {});
      if (map && result.lat && result.lng) {
        const latLng = [result.lat, result.lng];
        if (!marker) {
          marker = L.marker(latLng).addTo(map);
        } else {
          marker.setLatLng(latLng);
        }
        if (focusMap) map.flyTo(latLng, 10, { duration: 0.8 });
      }
    }

    async function reverseLookup(lat, lng) {
      try {
        const response = await fetch(
          `/api/locations/reverse?lat=${encodeURIComponent(lat)}&lng=${encodeURIComponent(lng)}`,
        );
        const data = await response.json();
        if (data?.result) applySelection(data.result, false);
      } catch (_) {
        /* noop */
      }
    }

    if (!enabled || !mapNode || !window.L) {
      if (mapNode) {
        mapNode.classList.add("is-disabled");
        mapNode.textContent = enabled
          ? "Map library is unavailable right now."
          : "Add GEOAPIFY_API_KEY to enable verified search and map selection.";
      }
      return;
    }

    map = L.map(mapNode, {
      zoomControl: true,
      scrollWheelZoom: true,
    }).setView([defaultView.lat, defaultView.lng], defaultView.zoom);

    L.tileLayer(
      "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
      {
        maxZoom: 19,
        attribution: "&copy; OpenStreetMap contributors &copy; CARTO",
      },
    ).addTo(map);

    const form = picker.closest("form");
    const currentCity = form?.querySelector('input[name="job_city"]')?.value;
    const currentState = form?.querySelector('input[name="job_state"]')?.value;
    const currentCountry = form?.querySelector(
      'input[name="job_country"]',
    )?.value;
    const existingLabel = [currentCity, currentState, currentCountry]
      .filter(Boolean)
      .join(", ");
    if (existingLabel && searchInput) searchInput.value = existingLabel;

    map.on("click", (event) => {
      const { lat, lng } = event.latlng;
      if (!marker) {
        marker = L.marker([lat, lng]).addTo(map);
      } else {
        marker.setLatLng([lat, lng]);
      }
      reverseLookup(lat, lng);
    });

    resetBtn?.addEventListener("click", () => {
      map.flyTo([defaultView.lat, defaultView.lng], defaultView.zoom, {
        duration: 0.8,
      });
    });

    if (searchInput) {
      searchInput.addEventListener("input", () => {
        clearTimeout(debounceId);
        const query = searchInput.value.trim();
        if (query.length < 3) {
          renderResults(resultsWrap, [], () => {});
          return;
        }

        debounceId = setTimeout(async () => {
          try {
            const cacheKey = query.toLowerCase();
            if (searchCache.has(cacheKey)) {
              renderResults(resultsWrap, searchCache.get(cacheKey), (result) =>
                applySelection(result),
              );
              return;
            }

            const response = await fetch(
              `/api/locations/search?query=${encodeURIComponent(query)}`,
            );
            const data = await response.json();
            const results = data.results || [];
            searchCache.set(cacheKey, results);
            renderResults(resultsWrap, results, (result) =>
              applySelection(result),
            );
          } catch (_) {
            renderResults(resultsWrap, [], () => {});
          }
        }, 450);
      });
    }

    picker.addEventListener("click", (event) => event.stopPropagation());
    document.addEventListener("click", () =>
      renderResults(resultsWrap, [], () => {}),
    );
  });
}

/* ── Form Validation ─────────────────────────────────────────── */
function initFormValidation() {
  document.querySelectorAll("form[data-validate]").forEach((form) => {
    form.addEventListener("submit", (e) => {
      let valid = true;
      form.querySelectorAll("[required]").forEach((field) => {
        const group = field.closest(".form-group");
        const err = group?.querySelector(".form-error-text");
        if (!field.value.trim()) {
          valid = false;
          field.classList.add("is-invalid");
          if (err) err.style.display = "block";
        } else {
          field.classList.remove("is-invalid");
          if (err) err.style.display = "none";
        }
      });
      if (!valid) {
        e.preventDefault();
        // Shake animation on the first invalid field
        const first = form.querySelector(".is-invalid");
        if (first) {
          first.style.animation = "none";
          first.offsetHeight;
          first.style.animation = "shake 0.4s ease";
        }
      }
    });

    form.querySelectorAll("[required]").forEach((field) => {
      field.addEventListener("input", () => {
        if (field.value.trim()) {
          field.classList.remove("is-invalid");
          const err = field
            .closest(".form-group")
            ?.querySelector(".form-error-text");
          if (err) err.style.display = "none";
        }
      });
    });
  });
}

// Add shake keyframes dynamically
const shakeStyle = document.createElement("style");
shakeStyle.textContent = `
  @keyframes shake {
    0%, 100% { transform: translateX(0); }
    15%       { transform: translateX(-5px); }
    30%       { transform: translateX(5px); }
    45%       { transform: translateX(-4px); }
    60%       { transform: translateX(4px); }
    75%       { transform: translateX(-2px); }
  }
`;
document.head.appendChild(shakeStyle);

/* ── Status Badge Sync ───────────────────────────────────────── */
function initStatusBadge() {
  const statusSelect = document.querySelector("#status-select");
  const statusBadge = document.querySelector("#status-badge");
  if (!statusSelect || !statusBadge) return;

  const map = {
    applied: "badge-applied",
    interview: "badge-interview",
    offer: "badge-offer",
    rejected: "badge-rejected",
    withdrawn: "badge-withdrawn",
    saved: "badge-saved",
  };

  statusSelect.addEventListener("change", () => {
    const val = statusSelect.value;
    statusBadge.className = "badge " + (map[val] || "badge-applied");
    const span = statusBadge.querySelector("span");
    if (span) span.textContent = val.charAt(0).toUpperCase() + val.slice(1);
    // Pop animation
    statusBadge.style.animation = "none";
    statusBadge.offsetHeight;
    statusBadge.style.animation =
      "badge-pop 0.3s cubic-bezier(0.34,1.56,0.64,1)";
  });

  const badgeAnim = document.createElement("style");
  badgeAnim.textContent = `@keyframes badge-pop { 0% { transform:scale(1); } 50% { transform:scale(1.25); } 100% { transform:scale(1); } }`;
  document.head.appendChild(badgeAnim);
}

/* ── Auto-resize Textarea ────────────────────────────────────── */
function initAutoResize() {
  document.querySelectorAll("textarea[data-auto-resize]").forEach((ta) => {
    const resize = () => {
      ta.style.height = "auto";
      ta.style.height = ta.scrollHeight + "px";
    };
    ta.addEventListener("input", resize);
    resize();
  });
}

/* ── Hero Parallax ───────────────────────────────────────────── */
function initHeroParallax() {
  const dashboard = document.querySelector(".hero-dashboard");
  const orbs = document.querySelectorAll(".hero-orb");
  if (!dashboard && !orbs.length) return;

  let ticking = false;
  window.addEventListener(
    "scroll",
    () => {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(() => {
        const sy = window.scrollY;
        if (dashboard) {
          dashboard.style.transform = `translateY(calc(-50% + ${sy * 0.2}px))`;
        }
        orbs.forEach((orb, i) => {
          const speed = 0.06 + i * 0.03;
          orb.style.transform = `translateY(${sy * speed}px)`;
        });
        ticking = false;
      });
    },
    { passive: true },
  );

  // Mouse parallax on hero
  const hero = document.querySelector(".hero");
  if (!hero) return;

  hero.addEventListener("mousemove", (e) => {
    const rect = hero.getBoundingClientRect();
    const cx = rect.width / 2;
    const cy = rect.height / 2;
    const mx = (e.clientX - rect.left - cx) / cx;
    const my = (e.clientY - rect.top - cy) / cy;

    orbs.forEach((orb, i) => {
      const depth = 8 + i * 6;
      orb.style.transform = `translate(${mx * depth}px, ${my * depth}px)`;
    });

    if (dashboard) {
      const base =
        parseFloat(
          dashboard.style.transform?.match(/\+(.+?)\)/) || [0, 0],
        )[1] || 0;
      dashboard.style.transform = `translateY(-50%) rotateY(${-4 + mx * 3}deg) rotateX(${2 + my * 2}deg)`;
    }
  });
}

/* ── Text Scramble on hero title ─────────────────────────────── */
function initTextScramble() {
  const target = document.querySelector("[data-scramble]");
  if (!target) return;

  const original = target.textContent;
  const chars = "!<>-_\\/[]{}—=+*^?#░▒▓";
  let frame = 0;
  let frameReq;

  function scramble() {
    const progress = Math.min(frame / 24, 1);
    let out = "";
    for (let i = 0; i < original.length; i++) {
      if (original[i] === " ") {
        out += " ";
        continue;
      }
      if (i / original.length < progress) {
        out += original[i];
      } else {
        out += chars[Math.floor(Math.random() * chars.length)];
      }
    }
    target.textContent = out;
    frame++;
    if (progress < 1) frameReq = requestAnimationFrame(scramble);
    else target.textContent = original;
  }

  // Run on page load
  setTimeout(() => requestAnimationFrame(scramble), 800);
}

/* ── Password Strength ───────────────────────────────────────── */
function initPasswordStrength(inputId = "password") {
  const input = document.getElementById(inputId);
  const bar = document.getElementById("pw-strength-bar");
  const label = document.getElementById("pw-strength-label");
  const wrap = document.getElementById("pw-strength");
  if (!input || !bar) return;

  input.addEventListener("input", () => {
    const val = input.value;
    if (!val) {
      if (wrap) wrap.style.display = "none";
      return;
    }
    if (wrap) wrap.style.display = "block";

    let s = 0;
    if (val.length >= 8) s++;
    if (val.length >= 12) s++;
    if (/[A-Z]/.test(val)) s++;
    if (/[0-9]/.test(val)) s++;
    if (/[^A-Za-z0-9]/.test(val)) s++;

    const levels = [
      { w: "20%", c: "var(--danger)", l: "Very weak" },
      { w: "40%", c: "var(--danger)", l: "Weak" },
      { w: "60%", c: "var(--warning)", l: "Fair" },
      { w: "80%", c: "var(--accent)", l: "Strong" },
      { w: "100%", c: "var(--success)", l: "Excellent" },
    ];

    const lvl = levels[Math.max(0, Math.min(s - 1, 4))];
    bar.style.width = lvl.w;
    bar.style.background = lvl.c;
    if (label) {
      label.textContent = lvl.l;
      label.style.color = lvl.c;
    }
  });
}

// Run if on register page
if (
  document.getElementById("password") &&
  document.getElementById("pw-strength-bar")
) {
  initPasswordStrength();
}

/* ── Toast ───────────────────────────────────────────────────── */
function showToast(message, type = "success", duration = 3500) {
  let container = document.querySelector(".toast-container");
  if (!container) {
    container = document.createElement("div");
    container.className = "toast-container";
    document.body.appendChild(container);
  }

  const icons = {
    success: `<svg viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clip-rule="evenodd"/></svg>`,
    error: `<svg viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 7.22z" clip-rule="evenodd"/></svg>`,
  };

  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `${icons[type] || ""} <span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.transition = "opacity 0.35s ease, transform 0.35s ease";
    toast.style.opacity = "0";
    toast.style.transform = "translateX(20px) scale(0.95)";
    setTimeout(() => toast.remove(), 360);
  }, duration);
}

/* ── Cursor sparkle (optional, subtle) ──────────────────────── */
function initCursorSparkle() {
  const dark = document.documentElement.getAttribute("data-theme") !== "light";
  if (window.matchMedia("(hover: none)").matches) return;

  window.addEventListener("click", (e) => {
    for (let i = 0; i < 6; i++) {
      const spark = document.createElement("div");
      const angle = ((Math.PI * 2) / 6) * i;
      const dist = 24 + Math.random() * 20;
      spark.style.cssText = `
        position:fixed; left:${e.clientX}px; top:${e.clientY}px;
        width:4px; height:4px; border-radius:50%;
        background:${dark ? "#f0c84a" : "#b8860b"};
        pointer-events:none; z-index:9999;
        box-shadow:0 0 6px ${dark ? "rgba(240,200,74,0.8)" : "rgba(184,134,11,0.8)"};
        transition: all 0.5s cubic-bezier(0.4,0,0.2,1);
        opacity:1;
      `;
      document.body.appendChild(spark);
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          spark.style.transform = `translate(${Math.cos(angle) * dist}px, ${Math.sin(angle) * dist}px) scale(0)`;
          spark.style.opacity = "0";
        });
      });
      setTimeout(() => spark.remove(), 500);
    }
  });
}

document.addEventListener("DOMContentLoaded", initCursorSparkle);

/* ── Expose global ───────────────────────────────────────────── */
window.Trackr = { showToast, showConfirmModal, toggleTheme };

/* ============================================================
   TRACKR — Premium Additions v3
   Cursor · Scroll Progress · Magnetic · Parallax · Split Text
   ============================================================ */

/* ── Custom Cursor ───────────────────────────────────────────── */
function initCustomCursor() {
  if (window.matchMedia("(hover: none)").matches) return;

  const dot = document.getElementById("cursor-dot");
  const ring = document.getElementById("cursor-ring");
  if (!dot || !ring) return;

  let mx = -100,
    my = -100,
    rx = -100,
    ry = -100;
  let rafId;

  document.addEventListener(
    "mousemove",
    (e) => {
      mx = e.clientX;
      my = e.clientY;
    },
    { passive: true },
  );

  function moveCursor() {
    // Dot follows instantly
    dot.style.left = mx + "px";
    dot.style.top = my + "px";
    // Ring lerps
    rx += (mx - rx) * 0.12;
    ry += (my - ry) * 0.12;
    ring.style.left = rx + "px";
    ring.style.top = ry + "px";
    rafId = requestAnimationFrame(moveCursor);
  }
  moveCursor();

  // Hide on leave, show on enter
  document.addEventListener("mouseleave", () => {
    dot.style.opacity = "0";
    ring.style.opacity = "0";
  });
  document.addEventListener("mouseenter", () => {
    dot.style.opacity = "1";
    ring.style.opacity = "1";
  });

  // Scale up on clickable elements
  const clickables =
    "a, button, .btn, .feature-card, .bento-card, .document-card, .step-card, .stat-card, input, select, textarea, label";
  document.querySelectorAll(clickables).forEach((el) => {
    el.addEventListener("mouseenter", () => {
      dot.style.width = "12px";
      dot.style.height = "12px";
      dot.style.background = "var(--accent-light)";
    });
    el.addEventListener("mouseleave", () => {
      dot.style.width = "8px";
      dot.style.height = "8px";
      dot.style.background = "var(--accent)";
    });
  });

  document.addEventListener("visibilitychange", () => {
    if (document.hidden) cancelAnimationFrame(rafId);
    else moveCursor();
  });
}

document.addEventListener("DOMContentLoaded", initCustomCursor);

/* ── Scroll Progress Bar ─────────────────────────────────────── */
function initScrollProgress() {
  const bar = document.getElementById("scroll-progress");
  if (!bar) return;
  window.addEventListener(
    "scroll",
    () => {
      const total = document.documentElement.scrollHeight - window.innerHeight;
      const pct = total > 0 ? (window.scrollY / total) * 100 : 0;
      bar.style.width = pct + "%";
    },
    { passive: true },
  );
}

document.addEventListener("DOMContentLoaded", initScrollProgress);

/* ── Magnetic Buttons ────────────────────────────────────────── */
function initMagneticButtons() {
  document.querySelectorAll(".btn-primary, .btn-lg").forEach((btn) => {
    btn.addEventListener("mousemove", (e) => {
      const rect = btn.getBoundingClientRect();
      const cx = rect.left + rect.width / 2;
      const cy = rect.top + rect.height / 2;
      const dx = (e.clientX - cx) * 0.28;
      const dy = (e.clientY - cy) * 0.28;
      btn.style.transform = `translate(${dx}px, ${dy}px) translateY(-2px)`;
    });
    btn.addEventListener("mouseleave", () => {
      btn.style.transform = "";
      btn.style.transition = "transform 0.5s cubic-bezier(0.34,1.56,0.64,1)";
      setTimeout(() => (btn.style.transition = ""), 500);
    });
    btn.addEventListener("mouseenter", () => {
      btn.style.transition = "transform 0.1s ease";
    });
  });
}

document.addEventListener("DOMContentLoaded", initMagneticButtons);

/* ── Animated Word Highlight ─────────────────────────────────── */
function initWordHighlight() {
  document.querySelectorAll(".word-highlight").forEach((el) => {
    setTimeout(() => el.classList.add("animate-highlight"), 600);
  });
}

document.addEventListener("DOMContentLoaded", initWordHighlight);

/* ── Split Text Animation for Hero ──────────────────────────── */
function initSplitText() {
  document.querySelectorAll("[data-split-text]").forEach((el) => {
    const text = el.textContent;
    el.innerHTML = "";
    el.classList.add("split-text");
    [...text].forEach((char, i) => {
      if (char === " ") {
        el.appendChild(document.createTextNode(" "));
        return;
      }
      const span = document.createElement("span");
      span.textContent = char;
      span.style.animationDelay = i * 0.03 + 0.3 + "s";
      el.appendChild(span);
    });
  });
}

document.addEventListener("DOMContentLoaded", initSplitText);

/* ── Parallax on scroll (landing page layers) ────────────────── */
function initScrollParallax() {
  const layers = document.querySelectorAll("[data-parallax]");
  if (!layers.length) return;

  let ticking = false;
  window.addEventListener(
    "scroll",
    () => {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(() => {
        const sy = window.scrollY;
        layers.forEach((el) => {
          const speed = parseFloat(el.dataset.parallax || 0.15);
          const offset = sy * speed;
          el.style.transform = `translateY(${offset}px)`;
        });
        ticking = false;
      });
    },
    { passive: true },
  );
}

document.addEventListener("DOMContentLoaded", initScrollParallax);

/* ── Bento card mouse tracking glow ─────────────────────────── */
function initBentoGlow() {
  document.querySelectorAll(".bento-card").forEach((card) => {
    card.addEventListener("mousemove", (e) => {
      const r = card.getBoundingClientRect();
      card.style.setProperty(
        "--mx",
        ((e.clientX - r.left) / r.width) * 100 + "%",
      );
      card.style.setProperty(
        "--my",
        ((e.clientY - r.top) / r.height) * 100 + "%",
      );
    });
  });
}

document.addEventListener("DOMContentLoaded", initBentoGlow);

/* ── Page transition on link click ──────────────────────────── */
function initPageTransitions() {
  document.querySelectorAll("a[href]").forEach((link) => {
    // Only same-origin, non-anchor, non-external links
    if (!link.href.startsWith(window.location.origin)) return;
    if (link.href.includes("#")) return;
    if (link.target === "_blank") return;

    link.addEventListener("click", (e) => {
      const href = link.href;
      e.preventDefault();
      document.body.style.transition =
        "opacity 0.25s ease, transform 0.25s ease";
      document.body.style.opacity = "0";
      document.body.style.transform = "scale(0.99)";
      setTimeout(() => {
        window.location.href = href;
      }, 240);
    });
  });
}

document.addEventListener("DOMContentLoaded", initPageTransitions);

/* ── Stat card counter with pop ─────────────────────────────── */
function initStatCounters() {
  const els = document.querySelectorAll(".stat-value[data-count]");
  if (!els.length) return;

  const obs = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        const el = entry.target;
        const end = parseInt(el.dataset.count, 10);
        let current = 0;
        const dur = 900;
        const start = performance.now();

        function tick(now) {
          const p = Math.min((now - start) / dur, 1);
          const v = Math.round(1 - Math.pow(1 - p, 4));
          current = Math.round(v * end);
          el.textContent = current;
          el.classList.add("counting");
          setTimeout(() => el.classList.remove("counting"), 200);
          if (p < 1) requestAnimationFrame(tick);
          else el.textContent = end;
        }

        requestAnimationFrame(tick);
        obs.unobserve(el);
      });
    },
    { threshold: 0.6 },
  );

  els.forEach((el) => obs.observe(el));
}

document.addEventListener("DOMContentLoaded", initStatCounters);

/* ── Smooth anchor scrolling ─────────────────────────────────── */
function initSmoothAnchors() {
  document.querySelectorAll('a[href^="#"]').forEach((a) => {
    a.addEventListener("click", (e) => {
      const id = a.getAttribute("href").slice(1);
      const el = document.getElementById(id);
      if (!el) return;
      e.preventDefault();
      el.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });
}

document.addEventListener("DOMContentLoaded", initSmoothAnchors);

/* ── Submit button loading state ────────────────────────────── */
function initButtonLoading() {
  document.querySelectorAll("form[data-validate]").forEach((form) => {
    form.addEventListener("submit", () => {
      const btn = form.querySelector('button[type="submit"]');
      if (btn && !form.querySelector(".is-invalid")) {
        setTimeout(() => btn.classList.add("btn-loading"), 10);
      }
    });
  });
}

document.addEventListener("DOMContentLoaded", initButtonLoading);
