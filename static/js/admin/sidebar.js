// ========================================
// SIDEBAR TOGGLE - FIXED
// ========================================

function toggleSidebar() {
  const sidebar = document.getElementById("sidebar");
  const overlay = document.getElementById("sidebarOverlay");
  const hamburgerIcon = document.querySelector(".hamburger-menu i");

  if (!sidebar) return;

  sidebar.classList.toggle("active");

  if (overlay) {
    overlay.classList.toggle("active");
  }

  if (hamburgerIcon) {
    if (sidebar.classList.contains("active")) {
      hamburgerIcon.className = "fa-solid fa-xmark";
    } else {
      hamburgerIcon.className = "fa-solid fa-bars";
    }
  }

  document.body.style.overflow = sidebar.classList.contains("active")
    ? "hidden"
    : "";
}

// Close sidebar when clicking overlay
document.addEventListener("DOMContentLoaded", function () {
  const overlay = document.getElementById("sidebarOverlay");
  if (overlay) {
    overlay.addEventListener("click", function () {
      if (this.classList.contains("active")) {
        toggleSidebar();
      }
    });
  }
});

// Close sidebar with Escape key
document.addEventListener("keydown", function (e) {
  if (e.key === "Escape") {
    const sidebar = document.getElementById("sidebar");
    if (sidebar && sidebar.classList.contains("active")) {
      toggleSidebar();
    }
  }
});

// Close sidebar when clicking a link (on mobile)
document.addEventListener("DOMContentLoaded", function () {
  const sidebarLinks = document.querySelectorAll(".sidebar-nav a");
  sidebarLinks.forEach(function (link) {
    link.addEventListener("click", function (e) {
      if (
        window.innerWidth <= 768 &&
        !this.classList.contains("sidebar-disabled")
      ) {
        const sidebar = document.getElementById("sidebar");
        if (sidebar && sidebar.classList.contains("active")) {
          setTimeout(function () {
            toggleSidebar();
          }, 300);
        }
      }
    });
  });
});

// Handle window resize
let resizeTimeout;
window.addEventListener("resize", function () {
  clearTimeout(resizeTimeout);
  resizeTimeout = setTimeout(function () {
    const sidebar = document.getElementById("sidebar");
    const overlay = document.getElementById("sidebarOverlay");
    const hamburgerIcon = document.querySelector(".hamburger-menu i");

    if (window.innerWidth > 768) {
      if (sidebar) sidebar.classList.remove("active");
      if (overlay) overlay.classList.remove("active");
      if (hamburgerIcon) hamburgerIcon.className = "fa-solid fa-bars";
      document.body.style.overflow = "";
    }
  }, 250);
});

// Touch support for swipe
let touchStartX = 0;
let touchEndX = 0;

document.addEventListener(
  "touchstart",
  function (e) {
    touchStartX = e.changedTouches[0].screenX;
  },
  { passive: true },
);

document.addEventListener(
  "touchend",
  function (e) {
    touchEndX = e.changedTouches[0].screenX;
    handleSwipe();
  },
  { passive: true },
);

function handleSwipe() {
  const swipeDistance = touchEndX - touchStartX;
  const sidebar = document.getElementById("sidebar");

  if (!sidebar) return;

  if (
    touchStartX < 50 &&
    swipeDistance > 80 &&
    !sidebar.classList.contains("active")
  ) {
    toggleSidebar();
  }

  if (swipeDistance < -80 && sidebar.classList.contains("active")) {
    toggleSidebar();
  }
}

// Initialize
document.addEventListener("DOMContentLoaded", function () {
  const sidebar = document.getElementById("sidebar");
  const overlay = document.getElementById("sidebarOverlay");

  if (window.innerWidth <= 768) {
    if (sidebar) sidebar.classList.remove("active");
    if (overlay) overlay.classList.remove("active");
    document.body.style.overflow = "";
  }
});

console.log("Sidebar JS loaded successfully!");
