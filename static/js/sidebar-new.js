// Completely new implementation of sidebar functionality
document.addEventListener('DOMContentLoaded', function() {
    // Essential DOM elements
    const sidebarWrapper = document.getElementById('sidebar-wrapper');
    const contentWrapper = document.getElementById('content-wrapper');
    const sidebarToggleBtn = document.getElementById('sidebarToggle');
    
    // Initialize sidebar based on screen size
    function initializeSidebar() {
        if (window.innerWidth <= 768) {
            // On mobile, always start with sidebar closed
            sidebarWrapper.classList.remove('collapsed');
            contentWrapper.classList.remove('sidebar-collapsed');
            localStorage.setItem('sidebarCollapsed', 'false');
        } else {
            // On desktop, check local storage for user preference
            const storedState = localStorage.getItem('sidebarCollapsed');
            if (storedState === 'true') {
                sidebarWrapper.classList.add('collapsed');
                contentWrapper.classList.add('sidebar-collapsed');
            } else {
                sidebarWrapper.classList.remove('collapsed');
                contentWrapper.classList.remove('sidebar-collapsed');
            }
        }
    }
    
    // Call once on page load
    initializeSidebar();
    
    // Handle sidebar toggle button click
    sidebarToggleBtn.addEventListener('click', function(e) {
        e.preventDefault();
        
        // Toggle classes
        sidebarWrapper.classList.toggle('collapsed');
        contentWrapper.classList.toggle('sidebar-collapsed');
        
        // Store current state in localStorage
        localStorage.setItem('sidebarCollapsed', sidebarWrapper.classList.contains('collapsed'));
    });
      // Handle dropdown menus - improved with better event handling
    const dropdownLinks = document.querySelectorAll('.sidebar-menu .dropdown-toggle');
    
    // Remove any existing event listeners (in case of page refresh)
    dropdownLinks.forEach(link => {
        const newLink = link.cloneNode(true);
        link.parentNode.replaceChild(newLink, link);
    });
    
    // Add click event listeners to dropdowns
    document.querySelectorAll('.sidebar-menu .dropdown-toggle').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Find the dropdown menu
            const dropdownMenu = this.nextElementSibling;
            
            // Toggle the current dropdown menu
            if (dropdownMenu) {
                dropdownMenu.classList.toggle('show');
                console.log('Toggling dropdown menu:', dropdownMenu);
            }
            
            // Close other dropdown menus
            document.querySelectorAll('.sidebar-menu .dropdown-menu.show').forEach(menu => {
                if (menu !== dropdownMenu) {
                    menu.classList.remove('show');
                }
            });
        });
    });
    
    // Special handling for dropdown menus when sidebar is collapsed (desktop only)
    const dropdowns = document.querySelectorAll('.sidebar-menu .dropdown');
    dropdowns.forEach(dropdown => {
        dropdown.addEventListener('mouseenter', function() {
            if (window.innerWidth > 768 && sidebarWrapper.classList.contains('collapsed')) {
                this.querySelector('.dropdown-menu').classList.add('show');
            }
        });
        
        dropdown.addEventListener('mouseleave', function() {
            if (window.innerWidth > 768 && sidebarWrapper.classList.contains('collapsed')) {
                this.querySelector('.dropdown-menu').classList.remove('show');
            }
        });
    });
    
    // Handle clicks outside sidebar on mobile to close it
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768) {
            if (!sidebarWrapper.contains(e.target) && 
                !sidebarToggleBtn.contains(e.target) && 
                sidebarWrapper.classList.contains('collapsed')) {
                
                sidebarWrapper.classList.remove('collapsed');
                contentWrapper.classList.remove('sidebar-collapsed');
                localStorage.setItem('sidebarCollapsed', 'false');
            }
        }
    });
    
    // Handle active menu items based on current page URL
    function setActiveMenuItem() {
        const currentPath = window.location.pathname;
        
        document.querySelectorAll('#sidebar-wrapper .nav-link').forEach(link => {
            const href = link.getAttribute('href');
            
            if (href && (currentPath === href || currentPath.startsWith(href) && href !== '/')) {
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
    }
    
    // Call this function on page load
    setActiveMenuItem();
    
    // Handle window resize events
    window.addEventListener('resize', function() {
        if (window.innerWidth <= 768) {
            // Ensure sidebar is closed on mobile by default
            sidebarWrapper.classList.remove('collapsed');
            contentWrapper.classList.remove('sidebar-collapsed');
        }
    });
});
