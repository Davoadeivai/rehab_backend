document.addEventListener('DOMContentLoaded', function () {
    // Initialize Select2
    $('#id_patient, #id_medication_type').select2({
        theme: 'bootstrap-5',
        placeholder: 'انتخاب کنید...',
        dir: 'rtl',
        language: 'fa',
        width: '100%'
    });

    const medicationTypeInput = $('#id_medication_type');
    const dailyDoseInput = $('#id_daily_dose');
    const treatmentDurationInput = $('#id_treatment_duration');
    const totalPrescribedInput = $('#id_total_prescribed');
    const startDateInput = $('#id_start_date');
    const endDateInput = $('#id_end_date');

    // Fetch default dose when medication changes
    medicationTypeInput.on('change', function () {
        const medicationId = $(this).val();
        if (medicationId) {
            fetch(`/patients/api/medication/${medicationId}/details/`)
                .then(response => response.json())
                .then(data => {
                    if (data.default_dose) {
                        dailyDoseInput.val(data.default_dose);
                        calculateTotal(); // Recalculate total
                    }
                })
                .catch(error => console.error('Error fetching medication details:', error));
        }
    });

    // Calculate total prescribed amount
    function calculateTotal() {
        const dailyDose = parseFloat(dailyDoseInput.val()) || 0;
        const duration = parseInt(treatmentDurationInput.val()) || 0;
        totalPrescribedInput.val((dailyDose * duration).toFixed(2));
    }

    // Calculate end date
    function calculateEndDate() {
        const startDate = startDateInput.val();
        const duration = treatmentDurationInput.val();

        if (startDate && duration) {
            // Basic validation for Jalali date format (YYYY/MM/DD)
            if (!/^\d{4}\/\d{1,2}\/\d{1,2}$/.test(startDate)) {
                return;
            }

            fetch(`/patients/api/calculate-end-date/?start_date=${startDate}&duration=${duration}`)
                .then(response => response.json())
                .then(data => {
                    if (data.end_date) {
                        endDateInput.val(data.end_date);
                    }
                })
                .catch(error => console.error('Error calculating end date:', error));
        }
    }

    // Event listeners for calculations
    dailyDoseInput.on('input', calculateTotal);
    treatmentDurationInput.on('input', function() {
        calculateTotal();
        calculateEndDate();
    });
    startDateInput.on('change', calculateEndDate); // Assuming date picker triggers change

    // Stepper functionality
    let currentStep = 1;
    const steps = document.querySelectorAll('.form-step');
    const stepperIcons = document.querySelectorAll('.stepper .step');
    const nextBtn = document.getElementById('next-btn');
    const prevBtn = document.getElementById('prev-btn');
    const submitBtn = document.getElementById('submit-btn');

    function showStep(stepNumber) {
        steps.forEach((step, index) => {
            step.classList.toggle('active', index + 1 === stepNumber);
        });

        stepperIcons.forEach((icon, index) => {
            icon.classList.remove('active', 'completed');
            if (index < stepNumber - 1) {
                icon.classList.add('completed');
            }
            if (index === stepNumber - 1) {
                icon.classList.add('active');
            }
        });

        prevBtn.style.display = stepNumber > 1 ? 'inline-block' : 'none';
        nextBtn.style.display = stepNumber < steps.length ? 'inline-block' : 'none';
        submitBtn.style.display = stepNumber === steps.length ? 'inline-block' : 'none';
    }

    function validateStep(stepNumber) {
        const currentStepFields = steps[stepNumber - 1].querySelectorAll('input, select, textarea');
        let isValid = true;
        currentStepFields.forEach(field => {
            if (!field.checkValidity()) {
                isValid = false;
                field.classList.add('is-invalid');
            } else {
                field.classList.remove('is-invalid');
            }
        });
        return isValid;
    }

    nextBtn.addEventListener('click', () => {
        if (validateStep(currentStep) && currentStep < steps.length) {
            currentStep++;
            showStep(currentStep);
        }
    });

    prevBtn.addEventListener('click', () => {
        if (currentStep > 1) {
            currentStep--;
            showStep(currentStep);
        }
    });

    showStep(currentStep);
});
