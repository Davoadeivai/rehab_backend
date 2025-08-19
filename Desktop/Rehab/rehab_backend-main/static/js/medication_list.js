document.addEventListener('DOMContentLoaded', function () {
    const deleteModal = document.getElementById('deleteMedicationModal');
    if (deleteModal) {
        deleteModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const medicationId = button.getAttribute('data-medication-id');
            const medicationName = button.getAttribute('data-medication-name');
            let deleteUrl = button.getAttribute('data-delete-url');

            const modalTitle = deleteModal.querySelector('.modal-title');
            const modalBody = deleteModal.querySelector('.modal-body');
            const deleteForm = deleteModal.querySelector('#deleteMedicationForm');

            modalTitle.textContent = `حذف داروی ${medicationName}`;
            modalBody.innerHTML = `آیا از حذف داروی <strong>${medicationName}</strong> اطمینان دارید؟ این عمل غیرقابل بازگشت است.`;
            deleteForm.action = deleteUrl;
        });
    }
});
