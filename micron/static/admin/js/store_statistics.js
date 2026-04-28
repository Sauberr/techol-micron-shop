document.addEventListener("DOMContentLoaded", function() {
    var rawDataElement = document.getElementById('chartData');
    if (!rawDataElement) return;

    var chartData = JSON.parse(rawDataElement.textContent);

    var ctx1 = document.getElementById('dailyChart').getContext('2d');
    new Chart(ctx1, {
        type: 'bar',
        data: {
            labels: chartData.daily.labels,
            datasets: [
                {
                    label: 'Revenue ($)',
                    type: 'line',
                    data: chartData.daily.revenue_data,
                    backgroundColor: 'rgba(46, 204, 113, 0.1)',
                    borderColor: 'rgba(46, 204, 113, 1)',
                    borderWidth: 3,
                    pointBackgroundColor: 'rgba(46, 204, 113, 1)',
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    fill: true,
                    tension: 0.4,
                    yAxisID: 'y'
                },
                {
                    label: 'Order Count',
                    type: 'bar',
                    data: chartData.daily.orders_data,
                    backgroundColor: 'rgba(54, 162, 235, 0.7)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 0,
                    borderRadius: 4,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    labels: { font: { size: 13, family: "'Helvetica Neue', 'Helvetica', 'Arial', sans-serif" } }
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: { display: true, text: 'Revenue ($)', font: { weight: 'bold' } },
                    grid: { borderDash: [4, 4], color: 'rgba(0,0,0,0.05)' },
                    beginAtZero: true
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: { display: true, text: 'Order Count', font: { weight: 'bold' } },
                    grid: { drawOnChartArea: false },
                    beginAtZero: true,
                    ticks: { stepSize: 1 }
                }
            }
        }
    });

    var ctx2 = document.getElementById('statusChart').getContext('2d');

    var statusColors = chartData.status.labels.map(function(label) {
        var lower = label.toLowerCase();
        if (lower === 'paid') {
            return 'rgba(46, 204, 113, 0.85)';
        } else if (lower === 'unpaid') {
            return 'rgba(231, 76, 60, 0.85)';
        } else {
            return 'rgba(241, 196, 15, 0.85)';
        }
    });

    new Chart(ctx2, {
        type: 'doughnut',
        data: {
            labels: chartData.status.labels,
            datasets: [{
                data: chartData.status.data,
                backgroundColor: statusColors,
                borderWidth: 0,
                hoverOffset: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '65%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { padding: 20, font: { size: 13 } }
                }
            }
        }
    });
});
