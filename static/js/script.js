const hamburger = document.querySelector(".hamburger");
const navMenu = document.querySelector("#nav-menu");

if (hamburger) {
  hamburger.addEventListener("click", () => {
    navMenu.classList.toggle("active");
  });
}

// ==========================================
// ADMIN LOGIN - DOUBLE CLICK ON LOGO
// ==========================================

document.addEventListener("DOMContentLoaded", function () {
  // Tafuta logo za mnyala
  const targets = [
    document.querySelector(".nav-logo"),
    document.querySelector(".header-logo.left"),
    document.querySelector(".company-title h1"),
  ];

  targets.forEach(function (target) {
    if (target) {
      let clickCount = 0;
      let clickTimer = null;

      target.style.cursor = "pointer";

      target.addEventListener("click", function (e) {
        if (e.target.closest("a")) {
          e.preventDefault();
        }

        clickCount++;

        if (clickTimer) {
          clearTimeout(clickTimer);
          clickTimer = null;
        }

        clickTimer = setTimeout(function () {
          clickCount = 0;
        }, 500);

        if (clickCount === 2) {
          // ==========================================
          // TUMIA URL DIRECT - HAPA NDIO SULUISHO
          // ==========================================
          window.location.href = "/auth/login";
          clickCount = 0;
        }
      });

      console.log("✅ Double click enabled on:", target);
    }
  });
});
