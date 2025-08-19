document.addEventListener('DOMContentLoaded', function () {
    // Initialize Select2 for all select elements
    function initializeSelect2() {
        $('select.select2').select2({
            theme: 'bootstrap-5',
            placeholder: 'انتخاب کنید...',
            dir: 'rtl',
            language: 'fa',
            width: '100%',
            dropdownAutoWidth: true
        });
    }

    // Initialize Select2 for initial form
    initializeSelect2();

    // Initialize datepickers with today's date as default
    const today = new Date();
    const jalaliToday = new persianDate(today).format('YYYY/MM/DD');
    
    $('.datepicker').each(function() {
        const $this = $(this);
        if (!$this.val()) {
            $this.val(jalaliToday);
        }
    }).persianDatepicker({
        format: 'YYYY/MM/DD',
        autoClose: true,
        initialValue: true,
        observer: true,
        timePicker: {
            enabled: false
        },
        toolbox: {
            calendarSwitch: {
                enabled: false
            }
        }
    });

    // Drug form management
    const drugForms = document.getElementById('drug-forms');
    const addButton = document.getElementById('add-drug');
    if (addButton) {
        // Hide and disable add button to enforce single drug
        addButton.style.display = 'none';
        addButton.disabled = true;
    }
    const totalForms = document.getElementById('id_drugs-TOTAL_FORMS');
    let formCount = parseInt(totalForms.value);

    // Remove drug add functionality: no-op
    function addDrugForm() { return; }

    // Remove handler if somehow attached
    if (addButton) {
        addButton.removeEventListener('click', addDrugForm);
    }
    
    // Remove drug form
    function removeDrugForm(event) {
        const form = event.target.closest('.drug-form');
        const deleteInput = form.querySelector('input[type="checkbox"][id$="-DELETE"]');
        
        if (deleteInput) {
            // Mark for deletion
            deleteInput.checked = true;
            form.style.display = 'none'; // Hide instead of remove
        } else {
            // If no delete input, remove immediately (for new forms)
            form.remove();
        }
        
        updateDrugNumbers();
    }
    
    // Update drug numbers in the UI
    function updateDrugNumbers() {
        const drugForms = document.querySelectorAll('.drug-form:visible');
        drugForms.forEach((form, index) => {
            const numberSpan = form.querySelector('.drug-number');
            if (numberSpan) {
                numberSpan.textContent = index + 1;
            }
        });
    }
    
    // Add event listeners for a drug form
    function addDrugFormEventListeners(formNum) {
        const medicationInput = $(`#id_drugs-${formNum}-medication`);
        const dosageInput = $(`#id_drugs-${formNum}-dosage`);
        const frequencyInput = $(`#id_drugs-${formNum}-frequency`);
        const durationDaysInput = $(`#id_drugs-${formNum}-duration_days`);
        const startDateInput = $(`#id_drugs-${formNum}-start_date`);
        const endDateInput = $(`#id_drugs-${formNum}-end_date`);
        
        // Fetch medication details when medication changes
        if (medicationInput.length) {
            medicationInput.on('change', function() {
                const medicationId = $(this).val();
                if (medicationId) {
                    fetch(`/patients/api/medication/${medicationId}/details/`)
                        .then(response => response.json())
                        .then(data => {
                            if (data.default_dose) {
                                dosageInput.val(data.default_dose);
                            }
                            if (data.default_unit) {
                                $(`#id_drugs-${formNum}-dosage_unit`).val(data.default_unit).trigger('change');
                            }
                        })
                        .catch(error => console.error('Error fetching medication details:', error));
                }
            });
        }
        
        // Calculate end date when duration or start date changes
        function calculateEndDate() {
            const startDate = startDateInput.val();
            const duration = durationDaysInput.val() || 1; // Default to 1 day if empty
            
            if (startDate) {
                // Basic validation for Jalali date format (YYYY/MM/DD)
                if (!/^\d{4}\/\d{1,2}\/\d{1,2}$/.test(startDate)) {
                    console.error('Invalid date format:', startDate);
                    return;
                }
                
                // Calculate end date client-side using persianDate library
                try {
                    const start = persianDate.parse(startDate, 'YYYY/MM/DD');
                    const end = start.add('days', parseInt(duration) - 1); // Subtract 1 to count start day
                    const endDateStr = end.format('YYYY/MM/DD');
                    
                    endDateInput.val(endDateStr);
                    // Update the date picker's displayed value
                    if (endDateInput.data('persianDatepicker')) {
                        endDateInput.persianDatepicker('setDate', [end.year(), end.month() + 1, end.date()]);
                    }
                    
                    console.log('Calculated end date:', endDateStr);
                } catch (error) {
                    console.error('Error calculating end date:', error);
                }
            }
        }
        
        // Add event listeners for calculations
        if (durationDaysInput.length && startDateInput.length) {
            durationDaysInput.on('input', calculateEndDate);
            startDateInput.on('change', calculateEndDate);
        }
    }
    
    // Initialize event listeners for existing forms
    document.querySelectorAll('.drug-form').forEach((form, index) => {
        const deleteButton = form.querySelector('.remove-drug');
        if (deleteButton) {
            deleteButton.addEventListener('click', removeDrugForm);
        }
        
        // Only initialize for non-empty forms
        if (form.style.display !== 'none') {
            // Set default start date if empty
            const startDateInput = form.querySelector('input[id$="-start_date"]');
            if (startDateInput && !startDateInput.value) {
                const today = new Date();
                const jalaliToday = new persianDate(today).format('YYYY/MM/DD');
                startDateInput.value = jalaliToday;
            }
            
            // Initialize form event listeners
            addDrugFormEventListeners(index);
            
            // Trigger initial end date calculation
            setTimeout(() => {
                const durationInput = form.querySelector('input[id$="-duration_days"]');
                if (durationInput) {
                    durationInput.dispatchEvent(new Event('input'));
                }
            }, 100);
        }
    });
    
    // Add new drug form when button is clicked
    if (addButton) {
        addButton.addEventListener('click', addDrugForm);
    }

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
        
        // Scroll to top of form when changing steps
        if (steps[stepNumber - 1]) {
            steps[stepNumber - 1].scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }

    function validateStep(stepNumber) {
        const currentStepFields = steps[stepNumber - 1].querySelectorAll('input:not([type="hidden"]):not([type="checkbox"]), select, textarea');
        let isValid = true;
        
        // Special validation for step 2 (drugs)
        if (stepNumber === 2) {
            const drugForms = document.querySelectorAll('.drug-form:visible');
            if (drugForms.length === 0) {
                // Show error if no drugs added
                const errorDiv = document.createElement('div');
                errorDiv.className = 'alert alert-danger';
                errorDiv.textContent = 'لطفاً حداقل یک دارو به نسخه اضافه کنید.';
                
                // Remove any existing error messages
                const existingError = steps[1].querySelector('.alert.alert-danger');
                if (existingError) {
                    existingError.remove();
                }
                
                steps[1].insertBefore(errorDiv, steps[1].firstChild);
                return false;
            }
            
            // Validate each drug form
            drugForms.forEach((form, index) => {
                const formInputs = form.querySelectorAll('input:not([type="hidden"]), select, textarea');
                formInputs.forEach(input => {
                    if (input.required && !input.value.trim()) {
                        isValid = false;
                        input.classList.add('is-invalid');
                        
                        // Add error message if not already present
                        if (!input.nextElementSibling || !input.nextElementSibling.classList.contains('invalid-feedback')) {
                            const errorDiv = document.createElement('div');
                            errorDiv.className = 'invalid-feedback';
                            errorDiv.textContent = 'این فیلد اجباری است.';
                            input.parentNode.insertBefore(errorDiv, input.nextSibling);
                        }
                    } else {
                        input.classList.remove('is-invalid');
                        // Remove error message if exists
                        if (input.nextElementSibling && input.nextElementSibling.classList.contains('invalid-feedback')) {
                            input.nextElementSibling.remove();
                        }
                    }
                });
            });
            
            return isValid;
        }
        
        // Default validation for other steps
        currentStepFields.forEach(field => {
            if (field.required && !field.value.trim()) {
                isValid = false;
                field.classList.add('is-invalid');
                
                // Add error message if not already present
                if (!field.nextElementSibling || !field.nextElementSibling.classList.contains('invalid-feedback')) {
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'invalid-feedback';
                    errorDiv.textContent = 'این فیلد اجباری است.';
                    field.parentNode.insertBefore(errorDiv, field.nextSibling);
                }
            } else if (field.type === 'email' && field.value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(field.value)) {
                // Email validation
                isValid = false;
                field.classList.add('is-invalid');
                
                if (!field.nextElementSibling || !field.nextElementSibling.classList.contains('invalid-feedback')) {
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'invalid-feedback';
                    errorDiv.textContent = 'لطفاً یک ایمیل معتبر وارد کنید.';
                    field.parentNode.insertBefore(errorDiv, field.nextSibling);
                }
            } else {
                field.classList.remove('is-invalid');
                // Remove error message if exists
                if (field.nextElementSibling && field.nextElementSibling.classList.contains('invalid-feedback')) {
                    field.nextElementSibling.remove();
                }
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
    
    // Handle form submission
    const prescriptionForm = document.querySelector('form.needs-validation');
    if (prescriptionForm) {
        prescriptionForm.addEventListener('submit', function(event) {
            if (!validateStep(currentStep)) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            this.classList.add('was-validated');
            
            // Show loading state
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                const originalText = submitBtn.innerHTML;
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>در حال ذخیره...';
                
                // Re-enable after 5 seconds if still processing
                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                }, 5000);
            }
        });
    }

    // Initialize the first step
    showStep(currentStep);
});
