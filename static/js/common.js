// Common JavaScript functionality for the College Management System
document.addEventListener('DOMContentLoaded', function() {
    // Add auto date to any element with class 'current-year'
    const yearElements = document.querySelectorAll('.current-year');
    if (yearElements.length > 0) {
        const currentYear = new Date().getFullYear();
        yearElements.forEach(el => el.textContent = currentYear);
    }
});
