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




function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const hamburger = document.getElementById('hamburgerMenu');
    const overlay = document.getElementById('sidebarOverlay');
    
    if (sidebar && hamburger && overlay) {
        sidebar.classList.toggle('active');
        hamburger.classList.toggle('active');
        overlay.classList.toggle('show');
        
        // Prevent body scroll when sidebar is open
        if (sidebar.classList.contains('active')) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = 'auto';
        }
    }
}

// Close sidebar on escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        const sidebar = document.querySelector('.sidebar');
        const hamburger = document.getElementById('hamburgerMenu');
        const overlay = document.getElementById('sidebarOverlay');
        
        if (sidebar && sidebar.classList.contains('active')) {
            sidebar.classList.remove('active');
            hamburger.classList.remove('active');
            overlay.classList.remove('show');
            document.body.style.overflow = 'auto';
        }
    }
});