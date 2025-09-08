document.addEventListener('DOMContentLoaded', function() {
    const calendarEl = document.getElementById('calendar');
    if (!calendarEl) {
        console.error('Calendar element not found!');
        return;
    }

    const appointmentsApiUrl = calendarEl.dataset.appointmentsApiUrl;
    const createAppointmentUrl = calendarEl.dataset.createAppointmentUrl;

    // Helper to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
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

    // Modals
    const addAppointmentModal = new bootstrap.Modal(document.getElementById('addAppointmentModal'));
    const eventDetailsModal = new bootstrap.Modal(document.getElementById('eventDetailsModal'));

    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        locale: 'fa',
        plugins: [ 'dayGrid', 'interaction', 'jalali' ], // Assuming 'jalali' is a valid plugin
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        buttonText: {
            today: 'امروز',
            month: 'ماه',
            week: 'هفته',
            day: 'روز',
            list: 'لیست'
        },
        titleFormat: {
            year: 'numeric',
            month: 'long'
        },
        events: appointmentsApiUrl,
        dateClick: function(info) {
            const dateInput = document.getElementById('dateInput');
            if (window.moment) { // Use moment-jalaali if available
                dateInput.value = moment(info.date).format('jYYYY/jMM/jDD');
            } else {
                dateInput.value = info.dateStr;
            }
            addAppointmentModal.show();
        },
        eventClick: function(info) {
            const event = info.event;
            document.getElementById('eventDetailsTitle').textContent = `جزئیات نوبت: ${event.title}`;
            document.getElementById('eventDetailsBody').innerHTML = `
                <p><strong>بیمار:</strong> ${event.title}</p>
                <p><strong>تاریخ:</strong> ${moment(event.start).format('jYYYY/jMM/jDD')}</p>
                <p><strong>مقدار دارو:</strong> ${event.extendedProps.amount}</p>
                <p><strong>وضعیت پرداخت:</strong> ${event.extendedProps.is_paid ? '<span class="badge bg-success">پرداخت شده</span>' : '<span class="badge bg-warning">پرداخت نشده</span>'}</p>
            `;
            eventDetailsModal.show();
        }
    });

    calendar.render();

    // Handle add appointment form submission
    document.getElementById('addAppointmentForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(this);
        const data = Object.fromEntries(formData.entries());

        fetch(createAppointmentUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            if (result.status === 'ok') {
                calendar.refetchEvents();
                addAppointmentModal.hide();
                loadAppointmentsTable();
                this.reset();
            } else {
                alert('خطا در ثبت نوبت: ' + (result.msg || 'خطای ناشناخته'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('خطای سیستمی در ثبت نوبت!');
        });
    });

    // Load appointments into the table
    function loadAppointmentsTable() {
        fetch(appointmentsApiUrl)
        .then(response => response.json())
        .then(events => {
            const tbody = document.getElementById('appointmentsTableBody');
            tbody.innerHTML = '';
            events.forEach(event => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${event.title}</td>
                    <td>${moment(event.start).format('jYYYY/jMM/jDD')}</td>
                    <td>${event.extendedProps.amount}</td>
                    <td>${event.extendedProps.is_paid ? '<span class="badge bg-success">پرداخت شده</span>' : '<span class="badge bg-warning">پرداخت نشده</span>'}</td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(error => console.error('Error loading appointments table:', error));
    }

    loadAppointmentsTable();
});
