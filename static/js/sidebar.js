// Sidebar functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize sidebar state from localStorage
    const sidebarState = localStorage.getItem('sidebarCollapsed');
    const sidebar = document.getElementById('sidebar-wrapper');
    const content = document.getElementById('content-wrapper');
    
    // For mobile view, initialize as closed
    if (window.innerWidth <= 768) {
        sidebar.classList.remove('collapsed');
        content.classList.remove('sidebar-collapsed');
        localStorage.setItem('sidebarCollapsed', 'false');
    }
    // For desktop view, use saved state
    else if (sidebarState === 'true') {
        sidebar.classList.add('collapsed');
        content.classList.add('sidebar-collapsed');
    }
    
    // Toggle sidebar
    document.getElementById('sidebarToggle').addEventListener('click', function(e) {
        e.preventDefault();
        
        sidebar.classList.toggle('collapsed');
        content.classList.toggle('sidebar-collapsed');
        
        // Force all dropdowns to close when toggling sidebar
        document.querySelectorAll('.sidebar-menu .dropdown-menu.show').forEach(menu => {
            menu.classList.remove('show');
        });
        
        // Save state to localStorage
        localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
        
        // Small delay to allow CSS transitions to complete
        setTimeout(function() {
            // Force browser to redraw the sidebar
            sidebar.style.display = 'none';
            sidebar.offsetHeight; // Force a reflow
            sidebar.style.display = '';
        }, 10);
    });
      // Handle dropdown behavior in sidebar
    const dropdowns = document.querySelectorAll('.sidebar-menu .dropdown');
    
    dropdowns.forEach(dropdown => {
        const link = dropdown.querySelector('.dropdown-toggle');
        const menu = dropdown.querySelector('.dropdown-menu');
        
        // For desktop: show dropdowns on hover when sidebar is collapsed
        dropdown.addEventListener('mouseenter', function() {
            if (window.innerWidth > 768 && document.getElementById('sidebar-wrapper').classList.contains('collapsed')) {
                menu.classList.add('show');
            }
        });
        
        dropdown.addEventListener('mouseleave', function() {
            if (window.innerWidth > 768 && document.getElementById('sidebar-wrapper').classList.contains('collapsed')) {
                menu.classList.remove('show');
            }
        });
        
        // Toggle dropdowns on click
        link.addEventListener('click', function(e) {
            if (!document.getElementById('sidebar-wrapper').classList.contains('collapsed') || window.innerWidth <= 768) {
                e.preventDefault();
                menu.classList.toggle('show');
            }
        });
    });
    
    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768) {
            const sidebar = document.getElementById('sidebar-wrapper');
            const sidebarToggle = document.getElementById('sidebarToggle');
            
            if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target) && sidebar.classList.contains('collapsed')) {
                sidebar.classList.remove('collapsed');
            }
        }
    });
    
    // Force expand all dropdowns when sidebar is collapsed and user hovers over items
    document.querySelectorAll('.sidebar-menu .dropdown').forEach(dropdown => {
        dropdown.addEventListener('mouseenter', function() {
            if (document.getElementById('sidebar-wrapper').classList.contains('collapsed') && window.innerWidth > 768) {
                dropdown.querySelector('.dropdown-menu').classList.add('show');
            }
        });
        
        dropdown.addEventListener('mouseleave', function() {
            if (document.getElementById('sidebar-wrapper').classList.contains('collapsed') && window.innerWidth > 768) {
                dropdown.querySelector('.dropdown-menu').classList.remove('show');
            }
        });
    });
});

// Handle active menu items
document.addEventListener('DOMContentLoaded', function() {
    // Get current URL path
    const currentPath = window.location.pathname;
    
    // Find links in the sidebar matching the current path
    const sidebarLinks = document.querySelectorAll('#sidebar-wrapper .nav-link');
    
    sidebarLinks.forEach(link => {
        const href = link.getAttribute('href');
        
        if (href && currentPath === href) {
            link.classList.add('active');
            
            // If it's in a dropdown, expand the dropdown
            const dropdown = link.closest('.dropdown');
            if (dropdown) {
                const dropdownMenu = dropdown.querySelector('.dropdown-menu');
                const dropdownToggle = dropdown.querySelector('.dropdown-toggle');
                
                if (dropdownMenu && dropdownToggle) {
                    dropdownMenu.classList.add('show');
                    dropdownToggle.classList.add('active');
                }
            }
        }
    });
});
