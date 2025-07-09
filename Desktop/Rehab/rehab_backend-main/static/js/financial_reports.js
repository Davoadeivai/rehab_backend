document.addEventListener('DOMContentLoaded', function() {
    // Global Chart.js settings
    Chart.defaults.font.family = 'Vazir';
    Chart.defaults.plugins.legend.position = 'bottom';
    Chart.defaults.plugins.legend.labels.padding = 20;
    Chart.defaults.plugins.legend.labels.font = {
        size: 12,
        weight: '500'
    };

    // Payment Type Chart
    const paymentTypeCanvas = document.getElementById('paymentTypeChart');
    if (paymentTypeCanvas) {
        try {
            const paymentTypeData = JSON.parse(paymentTypeCanvas.dataset.chartData);
            new Chart(paymentTypeCanvas.getContext('2d'), {
                type: 'doughnut',
                data: {
                    labels: paymentTypeData.map(item => item.payment_period),
                    datasets: [{
                        data: paymentTypeData.map(item => item.total),
                        backgroundColor: ['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b'],
                        borderWidth: 0,
                        hoverOffset: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            padding: 12,
                            titleFont: { size: 14, weight: '600' },
                            bodyFont: { size: 13 }
                        }
                    },
                    cutout: '70%'
                }
            });
        } catch (e) {
            console.error('Error parsing payment type chart data:', e);
            paymentTypeCanvas.parentElement.innerHTML = '<div class="alert alert-danger">خطا در بارگذاری نمودار.</div>';
        }
    }

    // Monthly Payments Chart
    const monthlyPaymentsCanvas = document.getElementById('monthlyPaymentsChart');
    if (monthlyPaymentsCanvas) {
        try {
            const monthlyPaymentsData = JSON.parse(monthlyPaymentsCanvas.dataset.chartData);
            new Chart(monthlyPaymentsCanvas.getContext('2d'), {
                type: 'bar',
                data: {
                    labels: monthlyPaymentsData.map(item => item.month),
                    datasets: [{
                        label: 'مبلغ پرداختی',
                        data: monthlyPaymentsData.map(item => item.total),
                        backgroundColor: '#4e73df',
                        borderRadius: 5,
                        borderSkipped: false
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            padding: 12,
                            titleFont: { size: 14, weight: '600' },
                            bodyFont: { size: 13 }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: { drawBorder: false },
                            ticks: { font: { size: 12 } }
                        },
                        x: {
                            grid: { display: false },
                            ticks: { font: { size: 12 } }
                        }
                    }
                }
            });
        } catch (e) {
            console.error('Error parsing monthly payments chart data:', e);
            monthlyPaymentsCanvas.parentElement.innerHTML = '<div class="alert alert-danger">خطا در بارگذاری نمودار.</div>';
        }
    }

    // Date filter functionality
    const filterButton = document.getElementById('filterBtn');
    if (filterButton) {
        filterButton.addEventListener('click', applyDateFilter);
    }
});

function applyDateFilter() {
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    const currentUrl = new URL(window.location.href);

    if (startDate) {
        currentUrl.searchParams.set('start_date', startDate);
    } else {
        currentUrl.searchParams.delete('start_date');
    }

    if (endDate) {
        currentUrl.searchParams.set('end_date', endDate);
    } else {
        currentUrl.searchParams.delete('end_date');
    }

    window.location.href = currentUrl.toString();
}
