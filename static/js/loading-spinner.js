document.addEventListener('DOMContentLoaded', function() {
    const loadingSpinner = document.getElementById('loading-spinner');

    if (loadingSpinner) {
        // Show loading spinner on AJAX requests
        document.addEventListener('ajaxStart', function() {
            loadingSpinner.style.display = 'flex';
        });

        document.addEventListener('ajaxStop', function() {
            loadingSpinner.style.display = 'none';
        });
    }
});
