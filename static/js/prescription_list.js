document.addEventListener('DOMContentLoaded', function () {
    // 1. Initialize tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

    // 2. Handle delete confirmation modal
    const deleteModal = document.getElementById('deletePrescriptionModal');
    if (deleteModal) {
        deleteModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const deleteUrl = button.getAttribute('data-delete-url');
            const prescriptionId = button.getAttribute('data-prescription-id');
            
            const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
            const modalTitle = deleteModal.querySelector('.modal-title');
            const modalBody = deleteModal.querySelector('.modal-body');

            if (confirmDeleteBtn && modalTitle && modalBody) {
                modalTitle.textContent = `تایید حذف نسخه شماره ${prescriptionId}`;
                modalBody.innerHTML = `<p>آیا از حذف این نسخه اطمینان دارید؟</p><p class="text-danger">این عمل غیرقابل بازگشت است.</p>`;
                confirmDeleteBtn.href = deleteUrl;
            }
        });
    }

    // 3. Preserve query parameters for pagination and filters
    const currentParams = new URLSearchParams(window.location.search);
    
    // Update pagination links
    const paginationLinks = document.querySelectorAll('.pagination a.page-link');
    paginationLinks.forEach(link => {
        const linkUrl = new URL(link.href);
        const pageNum = linkUrl.searchParams.get('page');
        const newParams = new URLSearchParams(currentParams);
        if (pageNum) {
            newParams.set('page', pageNum);
            link.href = `${linkUrl.pathname}?${newParams.toString()}`;
        }
    });

    // Update filter/sort links
    const filterLinks = document.querySelectorAll('.filter-dropdown a.dropdown-item');
    filterLinks.forEach(link => {
        const linkUrl = new URL(link.href);
        const linkKey = linkUrl.searchParams.keys().next().value;
        const linkValue = linkUrl.searchParams.values().next().value;
        
        const newParams = new URLSearchParams();
        // Preserve search query when changing filters
        if (currentParams.has('q')) {
            newParams.set('q', currentParams.get('q'));
        }
        newParams.set(linkKey, linkValue);
        
        link.href = `${linkUrl.pathname}?${newParams.toString()}`;
    });
});
