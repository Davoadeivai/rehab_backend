document.addEventListener('DOMContentLoaded', function () {
    const deleteModal = document.getElementById('deleteConfirmationModal');
    if (deleteModal) {
        deleteModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const deleteUrl = button.getAttribute('data-url');
            const modalForm = deleteModal.querySelector('#delete-form');
            if (modalForm) {
                modalForm.action = deleteUrl;
            }
        });
    }
});
