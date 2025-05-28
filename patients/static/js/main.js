// Main JavaScript file
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Initialize date pickers
    const dateInputs = document.querySelectorAll('.date-input');
    dateInputs.forEach(input => {
        new Pikaday({
            field: input,
            format: 'YYYY/MM/DD',
            yearRange: [1300, 1420],
            defaultDate: new Date(),
            setDefaultDate: true,
            // تنظیم تقویم به شمسی
            isRTL: true,
            onSelect: function(date) {
                // تبدیل تاریخ میلادی به شمسی
                const jDate = new JDate(date);
                const year = jDate.getFullYear();
                const month = (jDate.getMonth() + 1).toString().padStart(2, '0');
                const day = jDate.getDate().toString().padStart(2, '0');
                this._o.field.value = `${year}/${month}/${day}`;
            },
            toString(date, format) {
                // تبدیل تاریخ میلادی به شمسی
                const jDate = new JDate(date);
                const year = jDate.getFullYear();
                const month = (jDate.getMonth() + 1).toString().padStart(2, '0');
                const day = jDate.getDate().toString().padStart(2, '0');
                return `${year}/${month}/${day}`;
            },
            parse(dateString, format) {
                // تبدیل رشته تاریخ شمسی به آبجکت تاریخ
                if (!dateString) {
                    return null;
                }
                const [year, month, day] = dateString.split('/').map(Number);
                const jDate = new JDate(year, month - 1, day);
                return jDate.toGregorian();
            },
            i18n: {
                previousMonth: 'ماه قبل',
                nextMonth: 'ماه بعد',
                months: ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور', 'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'],
                weekdays: ['یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنجشنبه', 'جمعه', 'شنبه'],
                weekdaysShort: ['ی', 'د', 'س', 'چ', 'پ', 'ج', 'ش']
            }
        });
    });

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
});

// Custom alert function
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.querySelector('.alert-container').appendChild(alertDiv);
    setTimeout(() => alertDiv.remove(), 5000);
} 