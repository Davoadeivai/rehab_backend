document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Form validation
    (function () {
        'use strict'
        var forms = document.querySelectorAll('.needs-validation')
        Array.prototype.slice.call(forms)
            .forEach(function (form) {
                form.addEventListener('submit', function (event) {
                    if (!form.checkValidity()) {
                        event.preventDefault()
                        event.stopPropagation()
                    }
                    form.classList.add('was-validated')
                }, false)
            })
    })()

    // Initialize Select2
    $('#id_patient').select2({
        theme: 'bootstrap-5',
        placeholder: 'بیمار را انتخاب کنید',
        dir: 'rtl',
        language: 'fa',
        width: '100%'
    });

    $('#id_medication_type').select2({
        theme: 'bootstrap-5',
        placeholder: 'نوع دارو را انتخاب کنید',
        dir: 'rtl',
        language: 'fa',
        width: '100%'
    });

    // Date picker settings
    const dateFields = ['start_date', 'end_date'];
    dateFields.forEach(fieldName => {
        const input = document.getElementById('id_' + fieldName);
        if (input) {
            input.classList.add('date-input');
            input.setAttribute('dir', 'ltr');
            input.setAttribute('placeholder', 'مثال: ۱۴۰۴/۰۱/۰۱');
        }
    });

    // Auto-calculate total prescribed
    const dailyDoseInput = document.getElementById('id_daily_dose');
    const treatmentDurationInput = document.getElementById('id_treatment_duration');
    const totalPrescribedInput = document.getElementById('id_total_prescribed');

    function calculateTotal() {
        if (dailyDoseInput && treatmentDurationInput && totalPrescribedInput) {
            const dailyDose = parseFloat(dailyDoseInput.value) || 0;
            const duration = parseInt(treatmentDurationInput.value) || 0;
            totalPrescribedInput.value = (dailyDose * duration).toFixed(2);
        }
    }

    if (dailyDoseInput && treatmentDurationInput) {
        dailyDoseInput.addEventListener('input', calculateTotal);
        treatmentDurationInput.addEventListener('input', calculateTotal);
    }

    // Update stepper based on form progress
    function updateStepper() {
        const steps = document.querySelectorAll('.step');
        const patient = $('#id_patient').val();
        const medication = $('#id_medication_type').val();
        const dailyDose = $('#id_daily_dose').val();
        const duration = $('#id_treatment_duration').val();

        // Reset classes
        steps.forEach(step => {
            step.classList.remove('active', 'completed');
        });

        steps[0].classList.add('active'); // First step is always active initially

        if (patient) {
            steps[0].classList.add('completed');
            steps[1].classList.add('active');
        } else {
            return; // Stop if patient not selected
        }
        
        if (medication && dailyDose && duration) {
            steps[1].classList.add('completed');
            steps[2].classList.add('active');
        }
    }

    $('#id_patient, #id_medication_type, #id_daily_dose, #id_treatment_duration').on('change', updateStepper);
    
    // Initial call to set stepper state on page load (e.g., for edit forms)
    updateStepper();
});
