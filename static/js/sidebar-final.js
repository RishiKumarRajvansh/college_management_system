// Completely new sidebar JavaScript implementation
document.addEventListener('DOMContentLoaded', function() {
    const sidebarWrapper = document.getElementById('sidebar-wrapper');
    const contentWrapper = document.getElementById('content-wrapper');
    const sidebarToggle = document.getElementById('sidebarToggle');
    
    // Toggle sidebar
    sidebarToggle.addEventListener('click', function() {
        sidebarWrapper.classList.toggle('collapsed');
        contentWrapper.classList.toggle('sidebar-collapsed');
        
        // Save state to localStorage
        localStorage.setItem('sidebarCollapsed', sidebarWrapper.classList.contains('collapsed'));
        
        // Close all dropdowns when toggling sidebar
        document.querySelectorAll('.sidebar-menu .dropdown-menu').forEach(menu => {
            menu.classList.remove('show');
        });
    });
    
    // Load sidebar state from localStorage
    if (localStorage.getItem('sidebarCollapsed') === 'true' && window.innerWidth > 768) {
        sidebarWrapper.classList.add('collapsed');
        contentWrapper.classList.add('sidebar-collapsed');
    }
    
    // Handle dropdown toggles
    document.querySelectorAll('.sidebar-menu .dropdown-toggle').forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            
            const dropdownMenu = this.nextElementSibling;
            
            // Close all other dropdowns
            document.querySelectorAll('.sidebar-menu .dropdown-menu.show').forEach(menu => {
                if (menu !== dropdownMenu) {
                    menu.classList.remove('show');
                }
            });
            
            // Toggle this dropdown
            dropdownMenu.classList.toggle('show');
        });
    });
    
    // Hover effect for collapsed sidebar dropdowns (desktop only)
    if (window.innerWidth > 768) {
        document.querySelectorAll('.sidebar-menu .dropdown').forEach(dropdown => {
            dropdown.addEventListener('mouseenter', function() {
                if (sidebarWrapper.classList.contains('collapsed')) {
                    this.querySelector('.dropdown-menu').classList.add('show');
                }
            });
            
            dropdown.addEventListener('mouseleave', function() {
                if (sidebarWrapper.classList.contains('collapsed')) {
                    this.querySelector('.dropdown-menu').classList.remove('show');
                }
            });
        });
    }
    
    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768 && 
            !sidebarWrapper.contains(e.target) && 
            !sidebarToggle.contains(e.target) && 
            sidebarWrapper.classList.contains('collapsed')) {
            
            sidebarWrapper.classList.remove('collapsed');
            contentWrapper.classList.remove('sidebar-collapsed');
        }
    });
    
    // Handle active menu items based on current URL
    const currentPath = window.location.pathname;
    document.querySelectorAll('#sidebar-wrapper .nav-link').forEach(link => {
        const href = link.getAttribute('href');
        if (href && currentPath.includes(href) && href !== '/') {
            link.classList.add('active');
            
            // If it's in a dropdown, make the parent active too
            const dropdown = link.closest('.dropdown');
            if (dropdown) {
                dropdown.querySelector('.nav-link').classList.add('active');
            }
        }
    });
});
