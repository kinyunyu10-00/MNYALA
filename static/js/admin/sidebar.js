/* ==========================================
   SIDEBAR TOGGLE
========================================== */

const menuButton = document.querySelector(".menu-btn");

const sidebar = document.querySelector(".sidebar");

menuButton.addEventListener("click", () => {

    sidebar.classList.toggle("active");

});