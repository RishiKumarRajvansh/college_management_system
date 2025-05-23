// notifications.js - Enhanced client-side notification handler
document.addEventListener('DOMContentLoaded', function() {
    // Dashboard notification container
    const notificationContainer = document.getElementById('notificationContainer');
    // Dropdown notification container
    const dropdownContainer = document.getElementById('notificationDropdownContainer');
      const loadingElement = document.getElementById('loadingNotifications');
    const markAllReadBtn = document.getElementById('markAllRead');
    const markAllReadDropdownBtn = document.getElementById('markAllReadDropdown');
    
    // Create loading spinner
    function createLoadingSpinner() {
        const spinner = document.createElement('div');
        spinner.className = 'text-center py-3';
        spinner.innerHTML = `
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        `;
        return spinner;
    }
    
    // Function to load notifications
    function loadNotifications(showLoadingIndicator = true) {
        // Check if we're on a page with notifications
        if (!notificationContainer && !dropdownContainer) return;
        
        // Show loading if requested
        if (showLoadingIndicator) {
            if (notificationContainer) {
                notificationContainer.innerHTML = '';
                notificationContainer.appendChild(createLoadingSpinner());
            }
            
            if (dropdownContainer) {
                dropdownContainer.innerHTML = '';
                dropdownContainer.appendChild(createLoadingSpinner());
            }
        }
        
        fetch('/api/notifications/')
            .then(response => response.json())
            .then(data => {
                // Remove loading indicator
                if (loadingElement) {
                    loadingElement.remove();
                }
                  // Update notification counter in navbar if it exists
                const notificationCounter = document.getElementById('notificationCounter');
                if (notificationCounter) {
                    notificationCounter.textContent = data.unread_count || '';
                    notificationCounter.style.display = data.unread_count ? 'inline-block' : 'none';
                }
                
                // Function to create notification elements
                const createNotificationElements = (container) => {
                    if (!container) return;
                    
                    // Clear existing notifications
                    while (container.firstChild) {
                        container.removeChild(container.firstChild);
                    }
                      // Display notifications or empty message
                    if (data.notifications && data.notifications.length > 0) {
                        data.notifications.forEach(notification => {
                            const notificationElement = document.createElement('div');
                            notificationElement.className = `notification-item ${notification.read ? 'read' : 'unread'} bg-${notification.type}-subtle border-${notification.type} p-3 mb-2 rounded`;
                            notificationElement.dataset.id = notification.id;
                            
                            const contentHtml = `
                                <div class="d-flex align-items-center">
                                    <div class="notification-icon me-3">
                                        <i class="fas fa-${getIconForType(notification.type)} text-${notification.type}"></i>
                                    </div>
                                    <div class="notification-content flex-grow-1">
                                        <p class="mb-1">${notification.message}</p>
                                        <small class="text-muted">${notification.created_at}</small>
                                    </div>
                                    <div class="notification-actions">
                                        ${notification.read ? '' : '<button class="btn btn-sm btn-link mark-read" data-id="'+notification.id+'">Mark read</button>'}
                                    </div>
                                </div>
                            `;
                            
                            notificationElement.innerHTML = contentHtml;
                            
                            // Add click handler for notification link
                            if (notification.link) {
                                notificationElement.style.cursor = 'pointer';
                                notificationElement.addEventListener('click', function(e) {
                                    if (!e.target.closest('.notification-actions')) {
                                        window.location.href = notification.link;
                                    }
                                });
                            }
                            
                            container.appendChild(notificationElement);
                        });
                        
                        // Add event listeners to mark read buttons inside this container
                        container.querySelectorAll('.mark-read').forEach(button => {
                            button.addEventListener('click', function(e) {
                                e.preventDefault();
                                const notificationId = this.dataset.id;
                                markAsRead(notificationId);
                            });
                        });
                    } else {
                        container.innerHTML = '<div class="text-center py-3"><p class="text-muted">No notifications</p></div>';
                    }
                };
                
                // Create notifications in the main container if it exists
                if (notificationContainer) {
                    createNotificationElements(notificationContainer);
                }
                
                // Create notifications in the dropdown container if it exists
                if (dropdownContainer) {
                    createNotificationElements(dropdownContainer);
                }
            })
            .catch(error => {
                console.error('Error loading notifications:', error);
                notificationContainer.innerHTML = '<div class="text-center py-3"><p class="text-danger">Failed to load notifications</p></div>';
            });
    }
    
    // Function to mark a notification as read
    function markAsRead(notificationId) {
        fetch(`/api/notifications/mark-read/${notificationId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadNotifications(); // Reload notifications
            }
        })
        .catch(error => {
            console.error('Error marking notification as read:', error);
        });
    }
    
    // Function to mark all notifications as read
    function markAllAsRead() {
        fetch('/api/notifications/mark-read/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadNotifications(); // Reload notifications
            }
        })
        .catch(error => {
            console.error('Error marking all notifications as read:', error);
        });
    }
    
    // Helper function to get icon based on notification type
    function getIconForType(type) {
        switch (type) {
            case 'success': return 'check-circle';
            case 'warning': return 'exclamation-triangle';
            case 'danger': return 'times-circle';
            case 'info':
            default: return 'info-circle';
        }
    }
    
    // Helper function to get CSRF token from cookies
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
      // Set up event listeners
    if (markAllReadBtn) {
        markAllReadBtn.addEventListener('click', function(e) {
            e.preventDefault();
            markAllAsRead();
        });
    }
    
    // Set up event listener for dropdown mark all read button
    if (markAllReadDropdownBtn) {
        markAllReadDropdownBtn.addEventListener('click', function(e) {
            e.preventDefault();
            markAllAsRead();
        });
    }
    
    // Initial load of notifications
    loadNotifications();
    
    // Refresh notifications every 60 seconds
    setInterval(loadNotifications, 60000);
});
