// Sidebar link and dropdown handling without an external UI JavaScript bundle.
document.addEventListener('DOMContentLoaded', function() {
    const sidebarWrapper = document.getElementById('sidebar-wrapper');
    const contentWrapper = document.getElementById('content-wrapper');
    const sidebarToggle = document.getElementById('sidebarToggle');

    if (!sidebarWrapper || !contentWrapper || !sidebarToggle) {
        return;
    }

    function toggleSidebar() {
        sidebarWrapper.classList.toggle('collapsed');
        contentWrapper.classList.toggle('sidebar-collapsed');
        localStorage.setItem('sidebarCollapsed', sidebarWrapper.classList.contains('collapsed'));
    }

    sidebarToggle.addEventListener('click', function(event) {
        event.preventDefault();
        toggleSidebar();
    });

    document.querySelectorAll('.sidebar-menu .dropdown-toggle').forEach(function(toggle) {
        toggle.addEventListener('click', function(event) {
            event.preventDefault();
            const menu = toggle.nextElementSibling;
            if (!menu) {
                return;
            }
            document.querySelectorAll('.sidebar-menu .dropdown-menu.show').forEach(function(openMenu) {
                if (openMenu !== menu) {
                    openMenu.classList.remove('show');
                }
            });
            menu.classList.toggle('show');
        });
    });

    const currentPath = window.location.pathname;
    document.querySelectorAll('.sidebar-menu .nav-link, .sidebar-menu .dropdown-item').forEach(function(link) {
        const href = link.getAttribute('href');
        if (href && href !== '#' && (currentPath === href || (currentPath.startsWith(href) && href !== '/'))) {
            link.classList.add('active');
            const dropdown = link.closest('.dropdown');
            const toggle = dropdown && dropdown.querySelector('.dropdown-toggle');
            if (toggle) {
                toggle.classList.add('active');
            }
        }
    });
});
