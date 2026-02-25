// ========== CHART MANAGEMENT ==========
document.addEventListener('DOMContentLoaded', function() {
    console.log('Charts module loaded');
    
    // Initialize charts when they become visible
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                const section = mutation.target;
                if (section.classList.contains('active')) {
                    initializeSectionCharts(section.id);
                }
            }
        });
    });
    
    // Observe all sections
    document.querySelectorAll('.page-section').forEach(section => {
        observer.observe(section, { attributes: true });
    });
});

function initializeSectionCharts(sectionId) {
    switch(sectionId) {
        case 'dashboard-home':
            initializeDashboardCharts();
            break;
        case 'analytics':
            initializeAnalyticsCharts();
            break;
        case 'predictions':
            initializePredictionCharts();
            break;
        case 'recommendations':
            initializeRecommendationCharts();
            break;
    }
}

function initializeDashboardCharts() {
    createFatigueChart();
    createProductivityChart();
    createUsageChart();
}

function initializeAnalyticsCharts() {
    // These will be created by analytics.js
    // We just need to ensure they're properly sized
    setTimeout(() => {
        resizeAllCharts();
    }, 100);
}

function initializePredictionCharts() {
    createPredictionTrendChart();
}

function initializeRecommendationCharts() {
    createImpactChart();
}

// ========== CHART CREATION FUNCTIONS ==========
function createPredictionTrendChart() {
    const ctx = document.getElementById('predictionTrendChart');
    if (!ctx) return;
    
    if (window.predictionTrendChart) {
        window.predictionTrendChart.destroy();
    }
    
    const data = {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        datasets: [
            {
                label: 'Fatigue Level',
                data: [75, 70, 68, 65, 68, 72],
                borderColor: '#ef4444',
                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                tension: 0.4,
                fill: true,
                yAxisID: 'y'
            },
            {
                label: 'Productivity Loss',
                data: [16, 15, 14, 13, 12.5, 12],
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                tension: 0.4,
                fill: true,
                yAxisID: 'y1'
            }
        ]
    };
    
    window.predictionTrendChart = new Chart(ctx, {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    position: 'top'
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Fatigue Level (%)'
                    },
                    grid: {
                        color: 'rgba(0,0,0,0.05)'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Productivity Loss (hours)'
                    },
                    grid: {
                        drawOnChartArea: false
                    }
                }
            }
        }
    });
}

function createImpactChart() {
    const ctx = document.getElementById('impactChart');
    if (!ctx) return;
    
    if (window.impactChart) {
        window.impactChart.destroy();
    }
    
    const data = {
        labels: ['Current', '+1 Month', '+2 Months', '+3 Months'],
        datasets: [
            {
                label: 'Productivity Gain',
                data: [0, 5, 9, 15],
                backgroundColor: 'rgba(16, 185, 129, 0.8)',
                borderRadius: 10
            },
            {
                label: 'Fatigue Reduction',
                data: [0, 8, 15, 25],
                backgroundColor: 'rgba(102, 126, 234, 0.8)',
                borderRadius: 10
            }
        ]
    };
    
    window.impactChart = new Chart(ctx, {
        type: 'bar',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top'
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Improvement (%)'
                    },
                    grid: {
                        color: 'rgba(0,0,0,0.05)'
                    }
                }
            }
        }
    });
}

// ========== CHART UTILITIES ==========
function resizeAllCharts() {
    const charts = [
        window.fatigueChart,
        window.productivityChart,
        window.usageChart,
        window.dailyUsageChart,
        window.weeklyTrendsChart,
        window.appUsageChart,
        window.predictionTrendChart,
        window.impactChart
    ];
    
    charts.forEach(chart => {
        if (chart) {
            chart.resize();
        }
    });
}

// Handle window resize
window.addEventListener('resize', function() {
    resizeAllCharts();
});

// Handle tab visibility change
document.addEventListener('visibilitychange', function() {
    if (!document.hidden) {
        setTimeout(resizeAllCharts, 100);
    }
});