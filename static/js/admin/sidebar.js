// ========================================
// SIDEBAR TOGGLE FUNCTIONALITY - CLEAN
// ========================================

(function () {
  "use strict";

  // ========================================
  // SIDEBAR TOGGLE
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

  // ========================================
  // SIDEBAR DROPDOWN TOGGLE
  // ========================================
  function toggleDropdown(btn) {
    const dropdown = btn.closest(".sidebar-dropdown");
    if (!dropdown) return;

    dropdown.classList.toggle("active");

    // Close other dropdowns
    document.querySelectorAll(".sidebar-dropdown.active").forEach(function (d) {
      if (d !== dropdown) {
        d.classList.remove("active");
      }
    });
  }

  // ========================================
  // DOM CONTENT LOADED
  // ========================================
  document.addEventListener("DOMContentLoaded", function () {
    console.log("✅ Sidebar JS loaded");

    // 1. Auto-open dropdown if child is active
    document.querySelectorAll(".sidebar-dropdown").forEach(function (dropdown) {
      const hasActive = dropdown.querySelector("a.active");
      if (hasActive) {
        dropdown.classList.add("active");
      }
    });

    // 2. Close sidebar when clicking overlay
    const overlay = document.getElementById("sidebarOverlay");
    if (overlay) {
      overlay.addEventListener("click", function () {
        if (this.classList.contains("active")) {
          toggleSidebar();
        }
      });
    }

    // 3. Close sidebar when clicking a link (on mobile)
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
            }, 150);
          }
        }
      });
    });

    // 4. Initialize sidebar state
    const sidebar = document.getElementById("sidebar");
    if (window.innerWidth <= 768) {
      if (sidebar) sidebar.classList.remove("active");
      if (overlay) overlay.classList.remove("active");
      document.body.style.overflow = "";
    }
  });

  // ========================================
  // CLOSE SIDEBAR WITH ESCAPE KEY
  // ========================================
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      const sidebar = document.getElementById("sidebar");
      if (sidebar && sidebar.classList.contains("active")) {
        toggleSidebar();
      }
    }
  });

  // ========================================
  // HANDLE WINDOW RESIZE
  // ========================================
  let resizeTimeout = null;

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

  // ========================================
  // TOUCH SUPPORT FOR SWIPE
  // ========================================
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

  // ========================================
  // MAKE FUNCTIONS GLOBALLY ACCESSIBLE
  // ========================================
  window.toggleSidebar = toggleSidebar;
  window.toggleDropdown = toggleDropdown;

  console.log(" Sidebar JS initialized successfully");
})(); // End of IIFE
