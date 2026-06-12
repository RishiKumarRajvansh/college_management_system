// Complete sidebar behavior for Tailwind-styled pages.
document.addEventListener('DOMContentLoaded', function() {
    const sidebarWrapper = document.getElementById('sidebar-wrapper');
    const contentWrapper = document.getElementById('content-wrapper');
    const sidebarToggle = document.getElementById('sidebarToggle');

    if (!sidebarWrapper || !contentWrapper || !sidebarToggle) {
        return;
    }

    sidebarToggle.addEventListener('click', function(event) {
        event.preventDefault();
        sidebarWrapper.classList.toggle('collapsed');
        contentWrapper.classList.toggle('sidebar-collapsed');
        localStorage.setItem('sidebarCollapsed', sidebarWrapper.classList.contains('collapsed'));
    });

    if (localStorage.getItem('sidebarCollapsed') === 'true' && window.innerWidth > 768) {
        sidebarWrapper.classList.add('collapsed');
        contentWrapper.classList.add('sidebar-collapsed');
    }

    document.querySelectorAll('.sidebar-menu .dropdown-toggle').forEach(function(toggle) {
        toggle.addEventListener('click', function(event) {
            event.preventDefault();
            const menu = toggle.nextElementSibling;
            if (menu) {
                menu.classList.toggle('show');
            }
        });
    });

    document.addEventListener('click', function(event) {
        if (window.innerWidth <= 768 &&
            !sidebarWrapper.contains(event.target) &&
            !sidebarToggle.contains(event.target) &&
            sidebarWrapper.classList.contains('collapsed')) {
            sidebarWrapper.classList.remove('collapsed');
            contentWrapper.classList.remove('sidebar-collapsed');
        }
    });
});
