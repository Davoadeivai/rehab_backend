document.addEventListener('DOMContentLoaded', function() {
    // Global Chart.js settings
    Chart.defaults.font.family = 'Vazir';
    Chart.defaults.plugins.legend.position = 'bottom';
    Chart.defaults.plugins.tooltip.rtl = true;

    // Helper function to create charts
    function createChart(canvasId, chartType, label, dataMap) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;

        const chartDataContainer = document.getElementById(canvasId + 'Data');
        if (!chartDataContainer) {
            canvas.parentElement.innerHTML = '<div class="chart-loading-error">خطا: منبع داده نمودار یافت نشد.</div>';
            return;
        }

        try {
            const data = JSON.parse(chartDataContainer.textContent);
            new Chart(canvas.getContext('2d'), {
                type: chartType,
                data: {
                    labels: data.map(item => item[dataMap.labelKey]),
                    datasets: [{
                        label: label,
                        data: data.map(item => item[dataMap.dataKey]),
                        backgroundColor: dataMap.backgroundColor || '#4e73df',
                        borderColor: dataMap.borderColor || '#4e73df',
                        borderWidth: 1,
                        borderRadius: 5
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: { beginAtZero: true }
                    },
                    plugins: {
                        legend: { display: true },
                        tooltip: {
                            bodyFont: { family: 'Vazir' },
                            titleFont: { family: 'Vazir' }
                        }
                    }
                }
            });
        } catch (e) {
            console.error('Error parsing chart data for ' + canvasId + ':', e);
            canvas.parentElement.innerHTML = '<div class="chart-loading-error">خطا در بارگذاری اطلاعات نمودار.</div>';
        }
    }

    // Create Medication Distribution Chart
    createChart('medicationChart', 'bar', 'تعداد نسخه', {
        labelKey: 'medication_type__name',
        dataKey: 'count',
        backgroundColor: 'rgba(78, 115, 223, 0.8)',
        borderColor: 'rgba(78, 115, 223, 1)'
    });

    // Create Distribution by Type Chart
    createChart('distributionChart', 'bar', 'مقدار توزیع شده', {
        labelKey: 'prescription__medication_type__name',
        dataKey: 'total_amount',
        backgroundColor: 'rgba(28, 200, 138, 0.8)',
        borderColor: 'rgba(28, 200, 138, 1)'
    });
});
