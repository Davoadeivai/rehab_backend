document.addEventListener('DOMContentLoaded', function () {
    // General Chart.js settings
    Chart.defaults.font.family = 'Vazir';
    Chart.defaults.plugins.legend.position = 'bottom';
    Chart.defaults.plugins.legend.labels.padding = 20;
    Chart.defaults.plugins.legend.labels.font = { size: 12, weight: '500' };

    const chartObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const canvas = entry.target;
                const container = canvas.parentElement;
                const loadingSpinner = container.querySelector('.loading-spinner');
                const errorMessage = container.querySelector('.error-message');

                try {
                    const chartType = canvas.dataset.type;
                    const rawData = canvas.dataset.stats;
                    const chartData = JSON.parse(rawData);

                    if (loadingSpinner) loadingSpinner.style.display = 'none';

                    renderChart(canvas, chartType, chartData);

                } catch (error) {
                    console.error('Failed to render chart:', error);
                    if (loadingSpinner) loadingSpinner.style.display = 'none';
                    if (errorMessage) errorMessage.style.display = 'block';
                }
                
                observer.unobserve(canvas);
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.lazy-chart').forEach(canvas => {
        chartObserver.observe(canvas);
    });

    function renderChart(canvas, type, data) {
        const ctx = canvas.getContext('2d');
        let options, chartConfigData;

        if (type === 'doughnut') {
            chartConfigData = {
                labels: data.map(item => item.gender || 'نامشخص'),
                datasets: [{
                    data: data.map(item => item.count),
                    backgroundColor: ['#4e73df', '#1cc88a', '#36b9cc'],
                    borderWidth: 0,
                    hoverOffset: 4
                }]
            };
            options = {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: { legend: { position: 'bottom' } }
            };
        } else if (type === 'bar') {
            chartConfigData = {
                labels: data.map(item => item.treatment_type || 'نامشخص'),
                datasets: [{
                    label: 'تعداد بیماران',
                    data: data.map(item => item.count),
                    backgroundColor: '#4e73df',
                    borderRadius: 5,
                    borderSkipped: false
                }]
            };
            options = {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, grid: { drawBorder: false } },
                    x: { grid: { display: false } }
                }
            };
        }

        new Chart(ctx, { type, data: chartConfigData, options });
    }
});
