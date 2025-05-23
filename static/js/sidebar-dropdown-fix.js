// sidebar-dropdown-fix.js - Fix for sidebar dropdown menus
document.addEventListener('DOMContentLoaded', function() {
    const sidebarWrapper = document.getElementById('sidebar-wrapper');
    const contentWrapper = document.getElementById('content-wrapper');
    const sidebarToggle = document.getElementById('sidebarToggle');
    
    // Initialize Bootstrap dropdowns
    var dropdownElementList = [].slice.call(document.querySelectorAll('.dropdown-toggle'));
    var dropdownList = dropdownElementList.map(function (dropdownToggleEl) {
        return new bootstrap.Dropdown(dropdownToggleEl, {
            // Prevent automatic dropdown positioning that might cause overlapping
            autoClose: true
        });
    });
    
    // Add proper spacing between dropdowns when they're expanded
    document.querySelectorAll('.sidebar-menu .dropdown').forEach((dropdown, index) => {
        // Close other dropdowns when one is opened to prevent overlapping
        dropdown.addEventListener('show.bs.dropdown', function() {
            document.querySelectorAll('.sidebar-menu .dropdown').forEach((otherDropdown) => {
                if (otherDropdown !== dropdown && otherDropdown.classList.contains('show')) {
                    bootstrap.Dropdown.getInstance(otherDropdown.querySelector('.dropdown-toggle')).hide();
                }
            });
            
            // If the sidebar is not collapsed, ensure dropdown is properly positioned
            if (!sidebarWrapper.classList.contains('collapsed')) {
                // Reset any previously applied styles
                dropdown.querySelector('.dropdown-menu').style.position = '';
                dropdown.querySelector('.dropdown-menu').style.inset = '';
            }
        });
    });
    
    // Fix for links inside dropdowns - ensure they work properly
    document.querySelectorAll('.sidebar-menu .dropdown-item').forEach(link => {
        link.addEventListener('click', function(e) {
            // Don't stop propagation to allow the link to work
            if (this.getAttribute('href') && this.getAttribute('href') !== '#') {
                // Let the browser handle the link navigation
                return true;
            }
        });
    });
    
    // Toggle sidebar function
    function toggleSidebar() {
        sidebarWrapper.classList.toggle('collapsed');
        contentWrapper.classList.toggle('sidebar-collapsed');
        
        // Close any open dropdowns when toggling the sidebar
        document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
            const dropdownToggle = menu.previousElementSibling;
            if (dropdownToggle && bootstrap.Dropdown.getInstance(dropdownToggle)) {
                bootstrap.Dropdown.getInstance(dropdownToggle).hide();
            }
        });
        
        // Save state to localStorage
        localStorage.setItem('sidebarCollapsed', sidebarWrapper.classList.contains('collapsed'));
    }
    
    // Toggle sidebar on button click
    sidebarToggle.addEventListener('click', function(e) {
        e.preventDefault();
        toggleSidebar();
    });
    
    // Load sidebar state from localStorage
    if (localStorage.getItem('sidebarCollapsed') === 'true' && window.innerWidth > 768) {
        sidebarWrapper.classList.add('collapsed');
        contentWrapper.classList.add('sidebar-collapsed');
    }
    
    // Handle hover effect for collapsed sidebar on desktop
    if (window.innerWidth > 768) {
        document.querySelectorAll('.sidebar-menu .dropdown').forEach(dropdown => {
            dropdown.addEventListener('mouseenter', function() {
                if (sidebarWrapper.classList.contains('collapsed')) {
                    // Get the dropdown instance
                    const dropdownElement = this.querySelector('.dropdown-toggle');
                    if (dropdownElement) {
                        const dropdownInstance = bootstrap.Dropdown.getInstance(dropdownElement);
                        if (dropdownInstance) {
                            dropdownInstance.show();
                        }
                    }
                }
            });
            
            dropdown.addEventListener('mouseleave', function() {
                if (sidebarWrapper.classList.contains('collapsed')) {
                    const dropdownElement = this.querySelector('.dropdown-toggle');
                    if (dropdownElement) {
                        const dropdownInstance = bootstrap.Dropdown.getInstance(dropdownElement);
                        if (dropdownInstance) {
                            dropdownInstance.hide();
                        }
                    }
                }
            });
        });
    }
    
    // For mobile: Close sidebar when clicking outside
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768 && 
            !sidebarWrapper.contains(e.target) && 
            !sidebarToggle.contains(e.target) && 
            sidebarWrapper.classList.contains('collapsed')) {
            
            sidebarWrapper.classList.remove('collapsed');
            contentWrapper.classList.remove('sidebar-collapsed');
        }
    });
    
    // Highlight active menu items
    const currentPath = window.location.pathname;
    document.querySelectorAll('.sidebar-menu .nav-link, .sidebar-menu .dropdown-item').forEach(link => {
        const href = link.getAttribute('href');
        if (href && href !== '#' && (currentPath === href || currentPath.startsWith(href) && href !== '/')) {
            link.classList.add('active');
            
            // If it's in a dropdown, make the dropdown toggle active too
            const dropdown = link.closest('.dropdown');
            if (dropdown && dropdown.querySelector('.dropdown-toggle')) {
                dropdown.querySelector('.dropdown-toggle').classList.add('active');
            }
        }
    });
});
