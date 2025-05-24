// sidebar-hover-expand.js - Expands sidebar on hover when collapsed
document.addEventListener('DOMContentLoaded', function() {
    const sidebarWrapper = document.getElementById('sidebar-wrapper');
    const contentWrapper = document.getElementById('content-wrapper');
    
    // Function to expand sidebar
    function expandSidebar() {
        // Only expand if sidebar is currently collapsed
        if (sidebarWrapper.classList.contains('collapsed')) {
            // Add a special class to indicate hover expansion (different from regular expanded state)
            sidebarWrapper.classList.add('hover-expanded');
            
            // Remove collapsed class to expand the sidebar
            sidebarWrapper.classList.remove('collapsed');
            contentWrapper.classList.remove('sidebar-collapsed');
        }
    }
    
    // Function to collapse sidebar back
    function collapseSidebar() {
        // Only collapse if it was expanded via hover
        if (sidebarWrapper.classList.contains('hover-expanded')) {
            // Remove the hover expanded class
            sidebarWrapper.classList.remove('hover-expanded');
            
            // Remember the user's original preference from localStorage
            if (localStorage.getItem('sidebarCollapsed') === 'true') {
                sidebarWrapper.classList.add('collapsed');
                contentWrapper.classList.add('sidebar-collapsed');
            }
        }
    }
    
    // Add mouseenter event to expand sidebar when hovered
    sidebarWrapper.addEventListener('mouseenter', function(e) {
        // Only activate this feature on desktop screens
        if (window.innerWidth > 768) {
            expandSidebar();
        }
    });
    
    // Add mouseleave event to collapse sidebar when mouse leaves
    sidebarWrapper.addEventListener('mouseleave', function(e) {
        // Only activate this feature on desktop screens
        if (window.innerWidth > 768) {
            collapseSidebar();
        }
    });
    
    // Add additional CSS class to body to support hover transition
    document.body.classList.add('sidebar-hover-enabled');
});
