document.addEventListener('DOMContentLoaded', function() {
    const loadingSpinner = document.getElementById('loading-spinner');

    if (loadingSpinner) {
        const showSpinner = () => {
            loadingSpinner.classList.remove('d-none');
        };

        // Show spinner on form submissions that navigate away
        document.querySelectorAll('form').forEach(form => {
            if (form.target !== '_blank') {
                form.addEventListener('submit', showSpinner);
            }
        });

        // Show spinner for internal link clicks that navigate away
        document.querySelectorAll('a[href]').forEach(link => {
            // Ignore links that open in a new tab, are javascript calls, or are Bootstrap components
            if (link.hostname === window.location.hostname && link.target !== '_blank' && !link.href.startsWith('javascript:') && !link.hasAttribute('data-bs-toggle')) {
                link.addEventListener('click', (e) => {
                    if (e.ctrlKey || e.metaKey) return; // Don't show for new tab clicks
                    showSpinner();
                });
            }
        });

        // Hide spinner on page load, including back/forward navigation from cache
        window.addEventListener('pageshow', function(event) {
            loadingSpinner.classList.add('d-none');
        });
    }
});
