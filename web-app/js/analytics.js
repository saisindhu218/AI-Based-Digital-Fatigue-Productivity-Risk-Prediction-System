// ========== ANALYTICS CHARTS ==========

document.addEventListener('DOMContentLoaded', function () {
    console.log('Analytics module loaded');

    const analyticsSection = document.getElementById('analytics');
    if (!analyticsSection) return;

    // Prevent duplicate observers
    if (window.analyticsObserverAttached) return;
    window.analyticsObserverAttached = true;

    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                const section = mutation.target;

                // Only initialize once when activated
                if (section.id === 'analytics' && section.classList.contains('active')) {
                    if (!window.analyticsInitialized) {
                        window.analyticsInitialized = true;
                        initializeAnalyticsCharts();
                    }
                }
            }
        });
    });

    observer.observe(analyticsSection, { attributes: true });
});


// ========== MAIN INITIALIZER ==========
function initializeAnalyticsCharts() {
    console.log('Initializing analytics charts...');

    createDailyUsageChart();
    createWeeklyTrendsChart();
    createAppUsageChart();
    createFocusChart();
}


// ========== DAILY USAGE ==========
function createDailyUsageChart() {
    const ctx = document.getElementById('dailyUsageChart');
    if (!ctx) return;

    if (window.dailyUsageChart instanceof Chart) {
        window.dailyUsageChart.destroy();
    }

    window.dailyUsageChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [
                {
                    label: 'Screen Time (hours)',
                    data: [8.5, 7.2, 9.1, 8.8, 6.5, 4.2, 5.8],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102,126,234,0.1)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Productive Time (hours)',
                    data: [6.2, 5.8, 7.3, 6.9, 5.1, 2.8, 4.2],
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16,185,129,0.1)',
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });
}


// ========== WEEKLY ==========
function createWeeklyTrendsChart() {
    const ctx = document.getElementById('weeklyTrendsChart');
    if (!ctx) return;

    if (window.weeklyTrendsChart instanceof Chart) {
        window.weeklyTrendsChart.destroy();
    }

    window.weeklyTrendsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6'],
            datasets: [
                {
                    label: 'Fatigue Score',
                    data: [72, 68, 65, 70, 67, 63],
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239,68,68,0.1)',
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Productivity Index',
                    data: [78, 82, 85, 80, 83, 87],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102,126,234,0.1)',
                    fill: true,
                    tension: 0.4
                }
            ]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });
}


// ========== APP USAGE ==========
function createAppUsageChart() {
    const ctx = document.getElementById('appUsageChart');
    if (!ctx) return;

    if (window.appUsageChart instanceof Chart) {
        window.appUsageChart.destroy();
    }

    window.appUsageChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['VS Code', 'Chrome', 'Slack', 'Outlook', 'Teams', 'Other'],
            datasets: [{
                data: [12.5, 8.3, 6.2, 4.8, 3.9, 7.3],
                backgroundColor: [
                    '#667eea',
                    '#764ba2',
                    '#f59e0b',
                    '#10b981',
                    '#ef4444',
                    '#6b7280'
                ]
            }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });
}


// ========== FOCUS ==========
function createFocusChart() {
    const ctx = document.getElementById('focusChart');
    if (!ctx) return;

    if (window.focusChart instanceof Chart) {
        window.focusChart.destroy();
    }

    window.focusChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Focused', 'Distracted', 'Breaks'],
            datasets: [{
                data: [45, 35, 20],
                backgroundColor: ['#10b981', '#ef4444', '#f59e0b']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%'
        }
    });
}