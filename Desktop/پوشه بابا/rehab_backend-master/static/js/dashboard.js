document.addEventListener('DOMContentLoaded', function() {
    // Set current date in Persian
    const options = { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        calendar: 'persian',
        locale: 'fa-IR'
    };
    const today = new Date().toLocaleDateString('fa-IR', options);
    const dateElement = document.getElementById('current-date');
    if (dateElement) {
        dateElement.textContent = today;
    }

    // Initialize Visits Chart
    const visitsCtx = document.getElementById('visitsChart');
    if (visitsCtx) {
        new Chart(visitsCtx.getContext('2d'), {
            type: 'line',
            data: {
                labels: ['شنبه', 'یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنجشنبه', 'جمعه'],
                datasets: [{
                    label: 'تعداد مراجعات',
                    data: [12, 19, 15, 27, 22, 18, 10],
                    backgroundColor: 'rgba(67, 97, 238, 0.1)',
                    borderColor: 'rgba(67, 97, 238, 1)',
                    borderWidth: 2,
                    tension: 0.3,
                    fill: true,
                    pointBackgroundColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleFont: { family: 'Vazir', size: 13 },
                        bodyFont: { family: 'Vazir', size: 12 },
                        padding: 12,
                        rtl: true
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        },
                        ticks: {
                            stepSize: 5
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    // Initialize Medication Distribution Chart
    const medsCtx = document.getElementById('medicationChart');
    if (medsCtx) {
        new Chart(medsCtx.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ['مسکن‌ها', 'آنتی‌بیوتیک‌ها', 'ویتامین‌ها', 'دیگر موارد'],
                datasets: [{
                    data: [35, 25, 25, 15],
                    backgroundColor: [
                        'rgba(67, 97, 238, 0.8)',
                        'rgba(16, 185, 129, 0.8)',
                        'rgba(245, 158, 11, 0.8)',
                        'rgba(239, 68, 68, 0.8)'
                    ],
                    borderWidth: 0,
                    cutout: '70%'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        rtl: true,
                        labels: {
                            font: {
                                family: 'Vazir',
                                size: 12
                            },
                            padding: 15,
                            usePointStyle: true,
                            pointStyle: 'circle'
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleFont: { family: 'Vazir', size: 13 },
                        bodyFont: { family: 'Vazir', size: 12 },
                        padding: 12,
                        rtl: true
                    }
                }
            }
        });
    }
});
