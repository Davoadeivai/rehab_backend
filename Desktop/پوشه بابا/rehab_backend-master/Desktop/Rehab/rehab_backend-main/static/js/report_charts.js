document.addEventListener('DOMContentLoaded', function () {
    const chartContainers = document.querySelectorAll('.chart-container-wrapper');

    const chartObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const container = entry.target;
                const canvas = container.querySelector('canvas');
                const placeholder = container.querySelector('.chart-placeholder');
                
                if (canvas && !canvas.chart) { // Check if chart is not already initialized
                    initializeChart(canvas, placeholder);
                }
                observer.unobserve(container);
            }
        });
    }, { threshold: 0.1 });

    chartContainers.forEach(container => {
        chartObserver.observe(container);
    });

    function initializeChart(canvas, placeholder) {
        const loadingSpinner = placeholder.querySelector('.spinner-border');
        const errorMessage = placeholder.querySelector('.error-message');
        const retryButton = placeholder.querySelector('.retry-button');

        const showLoading = () => {
            placeholder.style.display = 'flex';
            loadingSpinner.style.display = 'block';
            errorMessage.style.display = 'none';
            canvas.style.display = 'none';
        };

        const showError = (message) => {
            placeholder.style.display = 'flex';
            loadingSpinner.style.display = 'none';
            errorMessage.querySelector('span').textContent = message;
            errorMessage.style.display = 'block';
            canvas.style.display = 'none';
        };

        const showChart = () => {
            placeholder.style.display = 'none';
            canvas.style.display = 'block';
        };

        retryButton.addEventListener('click', () => initializeChart(canvas, placeholder));

        showLoading();

        try {
            const type = canvas.dataset.chartType;
            const labelsData = JSON.parse(canvas.dataset.labels);
            const valuesData = JSON.parse(canvas.dataset.values);
            const chartLabel = canvas.dataset.chartLabel;

            if (!type || !labelsData || !valuesData || !chartLabel) {
                throw new Error('Missing chart data attributes.');
            }

            const chartConfig = {
                type: type,
                data: {
                    labels: labelsData,
                    datasets: [{
                        label: chartLabel,
                        data: valuesData,
                        backgroundColor: [
                            'rgba(78, 115, 223, 0.2)',
                            'rgba(40, 167, 69, 0.2)',
                            'rgba(255, 193, 7, 0.2)',
                            'rgba(23, 162, 184, 0.2)',
                            'rgba(220, 53, 69, 0.2)',
                            'rgba(246, 194, 62, 0.2)',
                            'rgba(111, 66, 193, 0.2)'
                        ],
                        borderColor: [
                            'rgb(78, 115, 223)',
                            'rgb(40, 167, 69)',
                            'rgb(255, 193, 7)',
                            'rgb(23, 162, 184)',
                            'rgb(220, 53, 69)',
                            'rgb(246, 194, 62)',
                            'rgb(111, 66, 193)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: type === 'pie' || type === 'doughnut' ? 'right' : 'top',
                        }
                    },
                    scales: type === 'bar' || type === 'line' ? {
                        y: {
                            beginAtZero: true
                        }
                    } : {}
                }
            };

            canvas.chart = new Chart(canvas.getContext('2d'), chartConfig);
            showChart();

        } catch (error) {
            console.error('Chart initialization failed:', error);
            showError('Failed to load chart data.');
        }
    }
});
