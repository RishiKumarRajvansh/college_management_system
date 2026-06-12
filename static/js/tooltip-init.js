// Keep native browser title tooltips available on Tailwind-styled controls.
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('[data-tooltip]').forEach(function(element) {
        if (element.dataset.tooltip && !element.getAttribute('title')) {
            element.setAttribute('title', element.dataset.tooltip);
        }
    });
});
