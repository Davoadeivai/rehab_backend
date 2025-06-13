// IIFE to avoid polluting the global scope
(function () {
    'use strict';

    // --- Bootstrap Form Validation ---
    const forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // --- Amount Formatting with Hidden Input ---
    const amountDisplay = document.getElementById('id_amount_display');
    const amountHidden = document.getElementById('id_amount');

    if (amountDisplay && amountHidden) {
        // On page load, format the initial value if it exists
        if (amountHidden.value) {
            const numericValue = parseInt(amountHidden.value, 10);
            if (!isNaN(numericValue)) {
                amountDisplay.value = numericValue.toLocaleString('fa-IR');
            }
        }

        amountDisplay.addEventListener('input', function () {
            // 1. Get the raw value and remove non-digit characters
            let numericValue = this.value.replace(/\D/g, '');

            // 2. Update the hidden input with the clean numeric value
            amountHidden.value = numericValue;

            // 3. Format the display value with commas
            if (numericValue) {
                this.value = parseInt(numericValue, 10).toLocaleString('fa-IR');
            } else {
                this.value = ''; // Keep it empty if no numbers
            }
        });
    }

    // --- Initialize Select2 for Patient Field ---
    $(document).ready(function() {
        $('#id_patient').select2({
            placeholder: 'بیمار را انتخاب کنید',
            dir: 'rtl',
            language: 'fa',
            theme: 'bootstrap-5',
            width: '100%'
        });
    });

})();
