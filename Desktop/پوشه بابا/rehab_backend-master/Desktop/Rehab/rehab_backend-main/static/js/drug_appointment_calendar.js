document.addEventListener('DOMContentLoaded', function() {
    console.log('jQuery loaded:', typeof $ !== 'undefined');
    console.log('FullCalendar loaded:', typeof FullCalendar !== 'undefined');

    // Helper to show toast notifications
    function showToast(type, msg) {
        const toast = document.getElementById(type + 'Toast');
        if (!toast) {
            console.error(`Toast element ${type}Toast not found`);
            return;
        }
        const body = document.getElementById(type + 'ToastBody');
        if (!body) {
            console.error(`Toast body element ${type}ToastBody not found`);
            return;
        }
        body.textContent = msg;
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
    }

    // Helper to get CSRF token
    function getCookie(name) {
        if (!document.cookie || typeof document.cookie !== 'string') {
            console.warn('No cookies available or document.cookie is not a string');
            return null;
        }
        let cookieValue = null;
        if (document.cookie.split(';').length > 0) {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    // Initialize select2 for patient search
    const patientSelect = document.getElementById('patientSelect');
    if (patientSelect && typeof $ !== 'undefined' && $.fn && $.fn.select2) {
        $(patientSelect).select2({
            placeholder: 'جستجوی بیمار...',
            dir: 'rtl',
            language: 'fa'
        });
        patientSelect.addEventListener('change', function() {
            const sel = this.options[this.selectedIndex];
            const infoDiv = document.getElementById('patientInfo');
            if (!infoDiv) {
                console.error('patientInfo element not found');
                return;
            }
            if (this.value) {
                infoDiv.style.display = 'block';
                infoDiv.innerHTML = `
                    <b>نام کامل:</b> ${sel.getAttribute('data-fullname') || ''}<br>
                    <b>کد بیمار:</b> ${sel.getAttribute('data-code') || ''}<br>
                    <b>شماره تماس:</b> ${sel.getAttribute('data-phone') || ''}<br>
                    <b>آدرس:</b> ${sel.getAttribute('data-address') || ''}`;
            } else {
                infoDiv.style.display = 'none';
                infoDiv.innerHTML = '';
            }
        });
    } else {
        console.error('patientSelect, jQuery, or select2 not found');
    }

    // Initialize persianDatepicker
    const dateInput = document.getElementById('dateInput');
    if (dateInput && typeof $ !== 'undefined' && $.fn && $.fn.persianDatepicker) {
        $(dateInput).persianDatepicker({
            format: 'YYYY/MM/DD',
            autoClose: true,
            minDate: new Date(),
            calendar: {
                persian: {
                    locale: 'fa',
                    showHint: true
                }
            }
        });
    } else {
        console.error('dateInput, jQuery, or persianDatepicker not found');
    }

    // Validate form
    function validateForm() {
        const form = document.getElementById('appointmentForm');
        if (!form) return false;
        const patientSelect = document.getElementById('patientSelect');
        const dateInput = document.getElementById('dateInput');
        const timeInput = document.getElementById('timeInput');
        const statusSelect = document.getElementById('statusSelect');
        if (!patientSelect || !dateInput || !timeInput || !statusSelect) return false;

        let isValid = true;
        if (!patientSelect.value) {
            patientSelect.classList.add('is-invalid');
            isValid = false;
        } else {
            patientSelect.classList.remove('is-invalid');
        }

        const today = moment().startOf('day');
        const inputDate = moment(dateInput.value, 'jYYYY/jMM/jDD');
        if (!inputDate.isValid() || inputDate.isBefore(today)) {
            dateInput.classList.add('is-invalid');
            isValid = false;
        } else {
            dateInput.classList.remove('is-invalid');
        }

        if (!timeInput.value) {
            timeInput.classList.add('is-invalid');
            isValid = false;
        } else {
            timeInput.classList.remove('is-invalid');
        }

        if (!statusSelect.value) {
            statusSelect.classList.add('is-invalid');
            isValid = false;
        } else {
            statusSelect.classList.remove('is-invalid');
        }

        return isValid;
    }

    // Initialize FullCalendar
    const calendarEl = document.getElementById('calendar');
    if (!calendarEl) {
        console.error('Calendar element not found');
        return;
    }
    const loadingSpinner = document.getElementById('loadingSpinner');
    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        locale: 'fa',
        plugins: ['dayGrid', 'timeGrid', 'interaction'],
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay filterScheduled,filterCompleted,filterCancelled,filterNoShow'
        },
        buttonText: {
            today: 'امروز',
            month: 'ماه',
            week: 'هفته',
            day: 'روز'
        },
        customButtons: {
            filterScheduled: {
                text: 'رزرو شده',
                click: function() {
                    calendar.getEvents().forEach(event => {
                        event.setProp('display', event.extendedProps.status === 'scheduled' ? 'auto' : 'none');
                    });
                    document.querySelectorAll('.fc-button').forEach(btn => btn.classList.remove('active'));
                    this.classList.add('active');
                }
            },
            filterCompleted: {
                text: 'تکمیل شده',
                click: function() {
                    calendar.getEvents().forEach(event => {
                        event.setProp('display', event.extendedProps.status === 'completed' ? 'auto' : 'none');
                    });
                    document.querySelectorAll('.fc-button').forEach(btn => btn.classList.remove('active'));
                    this.classList.add('active');
                }
            },
            filterCancelled: {
                text: 'لغو شده',
                click: function() {
                    calendar.getEvents().forEach(event => {
                        event.setProp('display', event.extendedProps.status === 'cancelled' ? 'auto' : 'none');
                    });
                    document.querySelectorAll('.fc-button').forEach(btn => btn.classList.remove('active'));
                    this.classList.add('active');
                }
            },
            filterNoShow: {
                text: 'عدم حضور',
                click: function() {
                    calendar.getEvents().forEach(event => {
                        event.setProp('display', event.extendedProps.status === 'no_show' ? 'auto' : 'none');
                    });
                    document.querySelectorAll('.fc-button').forEach(btn => btn.classList.remove('active'));
                    this.classList.add('active');
                }
            }
        },
        titleFormat: {
            year: 'numeric',
            month: 'long'
        },
        events: {
            url: '/appointments/api/',
            method: 'GET',
            extraParams: function() {
                return {
                    status: document.querySelector('.fc-button.active') ? document.querySelector('.fc-button.active').textContent : ''
                };
            },
            success: function() {
                if (loadingSpinner) loadingSpinner.style.display = 'none';
            },
            failure: function() {
                if (loadingSpinner) loadingSpinner.style.display = 'none';
                showToast('error', 'خطا در بارگذاری نوبت‌ها!');
            }
        },
        eventDidMount: function(info) {
            const status = info.event.extendedProps.status;
            if (status === 'completed') info.el.style.backgroundColor = '#28a745';
            else if (status === 'cancelled') info.el.style.backgroundColor = '#dc3545';
            else if (status === 'no_show') info.el.style.backgroundColor = '#ffc107';
            else info.el.style.backgroundColor = '#4e73df';

            // Add tooltip
            if (typeof tippy !== 'undefined') {
                tippy(info.el, {
                    content: `
                        <b>بیمار:</b> ${info.event.extendedProps.patient_name || ''}<br>
                        <b>زمان:</b> ${info.event.extendedProps.time || ''}<br>
                        <b>یادداشت:</b> ${info.event.extendedProps.notes || 'بدون یادداشت'}
                    `,
                    allowHTML: true,
                    theme: 'light-border',
                    placement: 'top'
                });
            }
        },
        eventWillMount: function() {
            if (loadingSpinner) loadingSpinner.style.display = 'block';
        },
        dateClick: function(info) {
            const form = document.getElementById('appointmentForm');
            if (!form) {
                console.error('appointmentForm not found');
                return;
            }
            form.reset();
            const modalTitle = document.getElementById('modalTitle');
            const appointmentId = document.getElementById('appointmentId');
            const deleteBtn = document.getElementById('deleteBtn');
            const patientInfo = document.getElementById('patientInfo');
            if (!modalTitle || !appointmentId || !deleteBtn || !patientInfo) {
                console.error('One or more modal elements not found');
                return;
            }
            modalTitle.textContent = 'ثبت نوبت جدید';
            appointmentId.value = '';
            deleteBtn.classList.add('d-none');
            patientInfo.style.display = 'none';
            patientInfo.innerHTML = '';
            const dateInput = document.getElementById('dateInput');
            if (!dateInput) {
                console.error('dateInput not found');
                return;
            }
            const date = moment(info.date).format('jYYYY/jMM/jDD');
            dateInput.value = date;
            const modal = new bootstrap.Modal(document.getElementById('appointmentModal'));
            modal.show();
        },
        eventClick: function(info) {
            fetch(`/appointments/detail/${info.event.id}/`)
                .then(response => response.json())
                .then(data => {
                    const modalTitle = document.getElementById('modalTitle');
                    const appointmentId = document.getElementById('appointmentId');
                    const patientSelect = document.getElementById('patientSelect');
                    const dateInput = document.getElementById('dateInput');
                    const statusSelect = document.getElementById('statusSelect');
                    const notesInput = document.getElementById('notesInput');
                    const timeInput = document.getElementById('timeInput');
                    const patientInfo = document.getElementById('patientInfo');
                    const deleteBtn = document.getElementById('deleteBtn');
                    if (!modalTitle || !appointmentId || !patientSelect || !dateInput || !statusSelect || !notesInput || !timeInput || !patientInfo || !deleteBtn) {
                        console.error('One or more modal elements not found');
                        return;
                    }
                    modalTitle.textContent = 'جزئیات/ویرایش نوبت';
                    appointmentId.value = data.id;
                    patientSelect.value = data.patient_id;
                    if (typeof $ !== 'undefined' && $.fn && $.fn.select2) {
                        $(patientSelect).trigger('change.select2');
                    }
                    dateInput.value = data.appointment_date.replace(/-/g, '/');
                    statusSelect.value = data.status;
                    notesInput.value = data.notes || '';
                    timeInput.value = data.time || '';
                    const sel = document.querySelector(`#patientSelect option[value='${data.patient_id}']`);
                    if (sel) {
                        patientInfo.style.display = 'block';
                        patientInfo.innerHTML = `
                            <b>نام کامل:</b> ${sel.getAttribute('data-fullname') || ''}<br>
                            <b>کد بیمار:</b> ${sel.getAttribute('data-code') || ''}<br>
                            <b>شماره تماس:</b> ${sel.getAttribute('data-phone') || ''}<br>
                            <b>آدرس:</b> ${sel.getAttribute('data-address') || ''}`;
                    }
                    deleteBtn.classList.remove('d-none');
                    const modal = new bootstrap.Modal(document.getElementById('appointmentModal'));
                    modal.show();
                })
                .catch(() => showToast('error', 'خطا در دریافت اطلاعات نوبت!'));
        }
    });
    calendar.render();
    console.log('Calendar rendered:', calendarEl.innerHTML.length > 0);

    // Handle form submission
    const appointmentForm = document.getElementById('appointmentForm');
    if (appointmentForm) {
        appointmentForm.addEventListener('submit', function(e) {
            e.preventDefault();
            if (!validateForm()) {
                showToast('error', 'لطفاً تمام فیلدهای مورد نیاز را به درستی پر کنید.');
                return;
            }
            const appointmentId = document.getElementById('appointmentId');
            const patientSelect = document.getElementById('patientSelect');
            const dateInput = document.getElementById('dateInput');
            const timeInput = document.getElementById('timeInput');
            const statusSelect = document.getElementById('statusSelect');
            const notesInput = document.getElementById('notesInput');
            if (!appointmentId || !patientSelect || !dateInput || !timeInput || !statusSelect || !notesInput) {
                console.error('One or more form elements not found');
                return;
            }
            const id = appointmentId.value;
            const url = id ? `/appointments/detail/${id}/` : '/appointments/create/';
            const method = id ? 'PUT' : 'POST';
            const data = {
                patient_id: patientSelect.value,
                date: dateInput.value,
                time: timeInput.value,
                status: statusSelect.value,
                notes: notesInput.value
            };

            if (loadingSpinner) loadingSpinner.style.display = 'block';
            fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (loadingSpinner) loadingSpinner.style.display = 'none';
                if (result.status === 'ok') {
                    calendar.refetchEvents();
                    bootstrap.Modal.getInstance(document.getElementById('appointmentModal')).hide();
                    showToast('success', id ? 'نوبت با موفقیت ویرایش شد.' : 'نوبت با موفقیت ثبت شد.');
                } else {
                    showToast('error', result.msg || 'خطا در ثبت/ویرایش نوبت!');
                }
            })
            .catch(() => {
                if (loadingSpinner) loadingSpinner.style.display = 'none';
                showToast('error', 'خطا در ثبت/ویرایش نوبت!');
            });
        });
    } else {
        console.error('appointmentForm not found');
    }

    // Handle delete button
    const deleteBtn = document.getElementById('deleteBtn');
    if (deleteBtn) {
        deleteBtn.addEventListener('click', function() {
            const appointmentId = document.getElementById('appointmentId');
            if (!appointmentId) {
                console.error('appointmentId not found');
                return;
            }
            const id = appointmentId.value;
            if (!id) return;
            if (!confirm('آیا از حذف این نوبت مطمئن هستید؟')) return;
            if (loadingSpinner) loadingSpinner.style.display = 'block';
            fetch(`/appointments/detail/${id}/`, {
                method: 'DELETE',
                headers: { 'X-CSRFToken': csrftoken }
            })
            .then(response => response.json())
            .then(result => {
                if (loadingSpinner) loadingSpinner.style.display = 'none';
                if (result.status === 'ok') {
                    calendar.refetchEvents();
                    bootstrap.Modal.getInstance(document.getElementById('appointmentModal')).hide();
                    showToast('success', 'نوبت با موفقیت حذف شد.');
                } else {
                    showToast('error', result.msg || 'خطا در حذف نوبت!');
                }
            })
            .catch(() => {
                if (loadingSpinner) loadingSpinner.style.display = 'none';
                showToast('error', 'خطا در حذف نوبت!');
            });
        });
    } else {
        console.error('deleteBtn not found');
    }
});