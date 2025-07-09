// IIFE to encapsulate Bootstrap form validation logic
(function () {
    'use strict';

    // Fetch all the forms we want to apply custom Bootstrap validation styles to
    var forms = document.querySelectorAll('.needs-validation');

    // Loop over them and prevent submission
    Array.prototype.slice.call(forms)
        .forEach(function (form) {
            form.addEventListener('submit', function (event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }

                form.classList.add('was-validated');
            }, false);
        });
})();

// Initialize Persian date pickers for designated input fields
document.addEventListener('DOMContentLoaded', function () {
    const dateFields = ['date_birth', 'admission_date', 'treatment_withdrawal_date'];

    dateFields.forEach(fieldName => {
        const input = document.getElementById('id_' + fieldName);
        if (input) {
            // Add a specific class for the main.js script to initialize the Persian date picker
            input.classList.add('date-input'); 
            input.setAttribute('dir', 'ltr'); // Set direction for consistent date format entry
            input.setAttribute('placeholder', 'YYYY/MM/DD');

            // NOTE: The original script attempted to convert existing Gregorian dates to Jalali.
            // This client-side conversion can be unreliable (e.g., `JDate` is not defined).
            // It is recommended to handle date formatting and conversion on the backend
            // and pass the correctly formatted string to the template.
            // The original logic has been removed to prevent errors.
        }
    });
});
