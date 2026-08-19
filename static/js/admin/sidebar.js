document.addEventListener("DOMContentLoaded", () => {

    const menuButton = document.querySelector(".menu-btn");
    const sidebar = document.querySelector(".sidebar");

    if (!menuButton || !sidebar) {
        return;
    }

    menuButton.addEventListener("click", () => {

        sidebar.classList.toggle("sidebar-open");

    });

});