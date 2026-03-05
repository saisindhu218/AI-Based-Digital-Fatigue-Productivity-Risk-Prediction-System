// ========== CHART MANAGEMENT ==========

document.addEventListener('DOMContentLoaded', function () {
    console.log('Charts module loaded');

    // Prevent duplicate observers
    if (window.chartObserverAttached) return;
    window.chartObserverAttached = true;

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

    document.querySelectorAll('.page-section').forEach(section => {
        observer.observe(section, { attributes: true });
    });
});


// ========== SECTION INITIALIZER ==========
function initializeSectionCharts(sectionId) {
    switch (sectionId) {
        case 'dashboard-home':
            initializeDashboardCharts();
            break;

        case 'analytics':
            // analytics.js handles creation
            setTimeout(resizeAllCharts, 100);
            break;

        case 'predictions':
            initializePredictionCharts();
            break;

        case 'recommendations':
            initializeRecommendationCharts();
            break;
    }
}


// ========== DASHBOARD ==========
function initializeDashboardCharts() {
    createFatigueChart();
    createProductivityChart();
    createUsageChart();
}


// ========== PREDICTIONS ==========
function initializePredictionCharts() {
    createPredictionTrendChart();
}


// ========== RECOMMENDATIONS ==========
function initializeRecommendationCharts() {
    createImpactChart();
}


// ========== CHART CREATION FUNCTIONS ==========

function createPredictionTrendChart() {
    const ctx = document.getElementById('predictionTrendChart');
    if (!ctx) return;

    if (window.predictionTrendChart instanceof Chart) {
        window.predictionTrendChart.destroy();
    }

    window.predictionTrendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: [
                {
                    label: 'Fatigue Level',
                    data: [75, 70, 68, 65, 68, 72],
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239,68,68,0.1)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Productivity Loss',
                    data: [16, 15, 14, 13, 12.5, 12],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102,126,234,0.1)',
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}



function createImpactChart() {
    const ctx = document.getElementById('impactChart');
    if (!ctx) return;

    if (window.impactChart instanceof Chart) {
        window.impactChart.destroy();
    }

    window.impactChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Current', '+1 Month', '+2 Months', '+3 Months'],
            datasets: [
                {
                    label: 'Productivity Gain',
                    data: [0, 5, 9, 15],
                    backgroundColor: 'rgba(16,185,129,0.8)',
                    borderRadius: 10
                },
                {
                    label: 'Fatigue Reduction',
                    data: [0, 8, 15, 25],
                    backgroundColor: 'rgba(102,126,234,0.8)',
                    borderRadius: 10
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}



// ========== UTILITIES ==========

function resizeAllCharts() {
    const charts = [
        window.fatigueChart,
        window.productivityChart,
        window.usageChart,
        window.dailyUsageChart,
        window.weeklyTrendsChart,
        window.appUsageChart,
        window.focusChart,
        window.predictionTrendChart,
        window.impactChart
    ];

    charts.forEach(chart => {
        if (chart && typeof chart.resize === 'function') {
            chart.resize();
        }
    });
}


// Resize when window resizes
window.addEventListener('resize', resizeAllCharts);


// Fix rendering when tab becomes visible
document.addEventListener('visibilitychange', function () {
    if (!document.hidden) {
        setTimeout(resizeAllCharts, 150);
    }
});