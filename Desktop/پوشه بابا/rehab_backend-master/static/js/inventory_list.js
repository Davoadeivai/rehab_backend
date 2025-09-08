document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Filter functionality
    const filterButtons = document.querySelectorAll('.filter-btn');
    const inventoryRows = document.querySelectorAll('.inventory-row');

    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Manage active state for buttons
            filterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');

            const filter = this.getAttribute('data-filter');

            inventoryRows.forEach(row => {
                if (filter === 'all' || row.getAttribute('data-status') === filter) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    });

    // History modal functionality
    const historyModal = document.getElementById('historyModal');
    const historyContent = document.getElementById('historyContent');

    historyModal.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;
        const itemId = button.getAttribute('data-item-id');
        const url = `/patients/inventory/${itemId}/history/`; // Adjust this URL to your actual endpoint

        // Show spinner while loading
        historyContent.innerHTML = `
            <div class="text-center py-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">در حال بارگذاری...</span>
                </div>
            </div>`;

        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.history && data.history.length > 0) {
                    let html = '';
                    data.history.forEach(entry => {
                        const changeClass = entry.change > 0 ? 'text-success' : 'text-danger';
                        const icon = entry.change > 0 ? 'fa-plus-circle' : 'fa-minus-circle';
                        html += `
                            <div class="history-item">
                                <div class="history-icon ${changeClass}"><i class="fas ${icon}"></i></div>
                                <div class="history-content">
                                    <strong>${entry.change}</strong> ${entry.notes ? ' - ' + entry.notes : ''}
                                </div>
                                <div class="history-date">${new Date(entry.timestamp).toLocaleString('fa-IR')}</div>
                            </div>`;
                    });
                    historyContent.innerHTML = html;
                } else {
                    historyContent.innerHTML = `
                        <div class="empty-state">
                            <i class="fas fa-box-open"></i>
                            <p>تاریخچه‌ای برای این آیتم یافت نشد.</p>
                        </div>`;
                }
            })
            .catch(error => {
                console.error('Error fetching history:', error);
                historyContent.innerHTML = `
                    <div class="alert alert-danger">خطا در بارگذاری تاریخچه.</div>`;
            });
    });
});
