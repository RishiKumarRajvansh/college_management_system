// sidebar-working.js - Complete fix for sidebar links
document.addEventListener('DOMContentLoaded', function() {
    const sidebarWrapper = document.getElementById('sidebar-wrapper');
    const contentWrapper = document.getElementById('content-wrapper');
    const sidebarToggle = document.getElementById('sidebarToggle');
    
    // Initialize Bootstrap dropdowns - remove our custom handling
    var dropdownElementList = [].slice.call(document.querySelectorAll('.dropdown-toggle'));
    var dropdownList = dropdownElementList.map(function (dropdownToggleEl) {
        return new bootstrap.Dropdown(dropdownToggleEl);
    });
    
    // Toggle sidebar function
    function toggleSidebar() {
        sidebarWrapper.classList.toggle('collapsed');
        contentWrapper.classList.toggle('sidebar-collapsed');
        
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
