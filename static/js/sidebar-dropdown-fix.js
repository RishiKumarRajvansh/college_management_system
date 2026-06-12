// Sidebar dropdown behavior kept framework-free for Tailwind-styled pages.
document.addEventListener('DOMContentLoaded', function() {
    const sidebarWrapper = document.getElementById('sidebar-wrapper');
    const contentWrapper = document.getElementById('content-wrapper');
    const sidebarToggle = document.getElementById('sidebarToggle');

    if (!sidebarWrapper || !contentWrapper || !sidebarToggle) {
        return;
    }

    function closeMenus(exceptMenu) {
        document.querySelectorAll('.sidebar-menu .dropdown-menu.show').forEach(function(menu) {
            if (menu !== exceptMenu) {
                menu.classList.remove('show');
            }
        });
    }

    function toggleSidebar() {
        sidebarWrapper.classList.toggle('collapsed');
        contentWrapper.classList.toggle('sidebar-collapsed');
        closeMenus();
        localStorage.setItem('sidebarCollapsed', sidebarWrapper.classList.contains('collapsed'));
    }

    sidebarToggle.addEventListener('click', function(event) {
        event.preventDefault();
        toggleSidebar();
    });

    if (localStorage.getItem('sidebarCollapsed') === 'true' && window.innerWidth > 768) {
        sidebarWrapper.classList.add('collapsed');
        contentWrapper.classList.add('sidebar-collapsed');
    }

    document.querySelectorAll('.sidebar-menu .dropdown-toggle').forEach(function(toggle) {
        toggle.addEventListener('click', function(event) {
            event.preventDefault();
            const menu = toggle.nextElementSibling;
            if (!menu) {
                return;
            }
            closeMenus(menu);
            menu.classList.toggle('show');
        });
    });

    document.querySelectorAll('.sidebar-menu .dropdown').forEach(function(dropdown) {
        dropdown.addEventListener('mouseenter', function() {
            const menu = dropdown.querySelector('.dropdown-menu');
            if (menu && window.innerWidth > 768 && sidebarWrapper.classList.contains('collapsed')) {
                menu.classList.add('show');
            }
        });

        dropdown.addEventListener('mouseleave', function() {
            const menu = dropdown.querySelector('.dropdown-menu');
            if (menu && window.innerWidth > 768 && sidebarWrapper.classList.contains('collapsed')) {
                menu.classList.remove('show');
            }
        });
    });

    document.addEventListener('click', function(event) {
        if (!event.target.closest('.sidebar-menu')) {
            closeMenus();
        }
    });
});
