document.addEventListener('DOMContentLoaded', function () {
    const deleteModal = document.getElementById('deletePaymentModal');
    if (deleteModal) {
        deleteModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const paymentId = button.getAttribute('data-payment-id');
            const deleteUrl = button.getAttribute('data-delete-url');
            
            const modalTitle = deleteModal.querySelector('.modal-title');
            const modalBody = deleteModal.querySelector('.modal-body');
            const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');

            modalTitle.textContent = 'حذف پرداخت شماره ' + paymentId;
            modalBody.innerHTML = `<p>آیا از حذف این پرداخت اطمینان دارید؟</p><p class="text-danger">این عمل غیرقابل بازگشت است.</p>`;
            confirmDeleteBtn.href = deleteUrl;
        });
    }
});
