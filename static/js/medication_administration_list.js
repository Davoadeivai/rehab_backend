document.addEventListener('DOMContentLoaded', function () {
    const deleteModal = document.getElementById('deleteAdministrationModal');
    if (deleteModal) {
        deleteModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const administrationId = button.getAttribute('data-administration-id');
            const patientName = button.getAttribute('data-patient-name');
            const medicationName = button.getAttribute('data-medication-name');
            let deleteUrl = button.getAttribute('data-delete-url');

            const modalTitle = deleteModal.querySelector('.modal-title');
            const modalBody = deleteModal.querySelector('.modal-body');
            const deleteForm = deleteModal.querySelector('#deleteAdministrationForm');

            modalTitle.textContent = `حذف تجویز دارو`;
            modalBody.innerHTML = `آیا از حذف تجویز داروی <strong>${medicationName}</strong> برای بیمار <strong>${patientName}</strong> اطمینان دارید؟ این عمل غیرقابل بازگشت است.`;
            deleteForm.action = deleteUrl;
        });
    }
});
