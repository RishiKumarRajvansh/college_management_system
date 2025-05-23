// notification-refresh.js - Additional notification refresh functionality
document.addEventListener('DOMContentLoaded', function() {
    const refreshNotificationsBtn = document.getElementById('refreshNotifications');
    
    if (refreshNotificationsBtn) {
        refreshNotificationsBtn.addEventListener('click', function() {
            const icon = this.querySelector('i');
            icon.classList.add('fa-spin');
            
            // Assuming notifications.js has already loaded and defined the loadNotifications function
            if (typeof loadNotifications === 'function') {
                loadNotifications(true);
            } else {
                // Fallback if function isn't globally available - reload the page
                const notificationContainer = document.getElementById('notificationContainer');
                if (notificationContainer) {
                    // Show loading spinner
                    notificationContainer.innerHTML = `
                        <div class="text-center py-3">
                            <div class="spinner-border text-primary" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                        </div>
                    `;
                    
                    // Reload via AJAX
                    fetch('/api/notifications/')
                        .then(response => response.json())
                        .then(data => {
                            // Wait until we refresh the page data
                            setTimeout(() => {
                                window.location.reload();
                            }, 500);
                        })
                        .catch(err => {
                            console.error('Failed to refresh notifications:', err);
                            window.location.reload();
                        });
                }
            }
            
            // Remove spinning animation after 1 second
            setTimeout(() => {
                icon.classList.remove('fa-spin');
            }, 1000);
        });
    }
});
