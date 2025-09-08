document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form.needs-validation');
    const toastContainer = document.querySelector('.toast-container');

    if (!form || !toastContainer) {
        console.error('Feedback form or toast container not found.');
        return;
    }

    // Helper to create and show a Bootstrap toast
    function showToast(message, type = 'success') {
        const toastEl = document.createElement('div');
        const toastId = `toast-${Date.now()}`;
        toastEl.id = toastId;
        toastEl.className = `toast align-items-center text-white bg-${type} border-0`;
        toastEl.setAttribute('role', 'alert');
        toastEl.setAttribute('aria-live', 'assertive');
        toastEl.setAttribute('aria-atomic', 'true');

        const icon = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-triangle';

        toastEl.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas ${icon} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;

        toastContainer.appendChild(toastEl);
        const toast = new bootstrap.Toast(toastEl, { delay: 5000 });
        toast.show();

        toastEl.addEventListener('hidden.bs.toast', () => {
            toastEl.remove();
        });
    }

    // Handle form submission with AJAX
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        event.stopPropagation();

        if (!form.checkValidity()) {
            form.classList.add('was-validated');
            return;
        }

        const formData = new FormData(form);
        const submitButton = form.querySelector('button[type="submit"]');
        const originalButtonText = submitButton.innerHTML;
        submitButton.disabled = true;
        submitButton.innerHTML = `
            <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            در حال ارسال...
        `;

        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value,
                'X-Requested-With': 'XMLHttpRequest' // To identify AJAX requests in Django
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast(data.message || 'پیام شما با موفقیت ارسال شد.', 'success');
                form.reset();
                form.classList.remove('was-validated');
            } else {
                showToast(data.message || 'خطا در ارسال پیام. لطفاً دوباره تلاش کنید.', 'danger');
            }
        })
        .catch(error => {
            console.error('Submission error:', error);
            showToast('یک خطای پیش‌بینی نشده رخ داد. لطفاً با پشتیبانی تماس بگیرید.', 'danger');
        })
        .finally(() => {
            submitButton.disabled = false;
            submitButton.innerHTML = originalButtonText;
        });
    });
});
