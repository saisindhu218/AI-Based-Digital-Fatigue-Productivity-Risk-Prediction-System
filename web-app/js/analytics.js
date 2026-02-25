// ========== ANALYTICS PAGE ==========
document.addEventListener('DOMContentLoaded', function() {
    console.log('Analytics module loaded');
    
    // Only run on analytics page
    if (!document.getElementById('analytics')) return;
    
    loadAnalyticsData();
});

async function loadAnalyticsData() {
    try {
        // Show loading state
        showNotification('Loading analytics data...', 'info');
        
        // Fetch analytics data
        const data = await fetchAnalyticsData();
        
        // Create charts
        createDetailedCharts(data);
        
        // Update metrics
        updateMetrics(data);
        
        showNotification('Analytics data loaded', 'success');
    } catch (error) {
        console.error('Failed to load analytics:', error);
        showNotification('Could not load analytics data', 'error');
    }
}

async function fetchAnalyticsData() {
    // Mock data - replace with actual API call
    return {
        dailyUsage: {
            labels: ['6 AM', '9 AM', '12 PM', '3 PM', '6 PM', '9 PM', '12 AM'],
            work: [2, 4, 3, 2, 1, 0, 0],
            social: [0, 1, 2, 3, 2, 3, 1],
            entertainment: [0, 0, 1, 2, 3, 4, 2]
        },
        weeklyTrends: {
            labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
            fatigue: [70, 65, 68, 72],
            productivity: [15, 14, 13, 12],
            screenTime: [9, 8.5, 8.2, 8.0]
        },
        appUsage: {
            labels: ['Slack', 'VS Code', 'Chrome', 'Spotify', 'Teams', 'Other'],
            data: [25, 20, 18, 12, 10, 15]
        },
        metrics: {
            avgDailyUsage: 8.2,
            peakHours: '2-4 PM',
            mostUsedApp: 'Slack (25%)',
            focusRatio: '42%',
            breakFrequency: 'Every 45min'
        }
    };
}

function createDetailedCharts(data) {
    createDailyUsageChart(data.dailyUsage);
    createWeeklyTrendsChart(data.weeklyTrends);
    createAppUsageChart(data.appUsage);
}

function createDailyUsageChart(dailyData) {
    const ctx = document.getElementById('dailyUsageChart');
    if (!ctx) return;
    
    // Destroy existing chart
    if (window.dailyUsageChart) {
        window.dailyUsageChart.destroy();
    }
    
    window.dailyUsageChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: dailyData.labels,
            datasets: [
                {
                    label: 'Work',
                    data: dailyData.work,
                    backgroundColor: 'rgba(102, 126, 234, 0.8)',
                    borderRadius: 5
                },
                {
                    label: 'Social',
                    data: dailyData.social,
                    backgroundColor: 'rgba(118, 75, 162, 0.8)',
                    borderRadius: 5
                },
                {
                    label: 'Entertainment',
                    data: dailyData.entertainment,
                    backgroundColor: 'rgba(245, 158, 11, 0.8)',
                    borderRadius: 5
                }
            ]
        },
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
                    stacked: false,
                    grid: {
                        display: false
                    }
                },
                y: {
                    stacked: false,
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Hours'
                    },
                    grid: {
                        color: 'rgba(0,0,0,0.05)'
                    }
                }
            }
        }
    });
}

function createWeeklyTrendsChart(weeklyData) {
    const ctx = document.getElementById('weeklyTrendsChart');
    if (!ctx) return;
    
    if (window.weeklyTrendsChart) {
        window.weeklyTrendsChart.destroy();
    }
    
    window.weeklyTrendsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: weeklyData.labels,
            datasets: [
                {
                    label: 'Fatigue Level',
                    data: weeklyData.fatigue,
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Productivity Loss',
                    data: weeklyData.productivity,
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Screen Time',
                    data: weeklyData.screenTime,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    grid: {
                        color: 'rgba(0,0,0,0.05)'
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

function createAppUsageChart(appData) {
    const ctx = document.getElementById('appUsageChart');
    if (!ctx) return;
    
    if (window.appUsageChart) {
        window.appUsageChart.destroy();
    }
    
    window.appUsageChart = new Chart(ctx, {
        type: 'polarArea',
        data: {
            labels: appData.labels,
            datasets: [{
                data: appData.data,
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
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right'
                }
            }
        }
    });
}

function updateMetrics(metrics) {
    const metricElements = {
        'avg-daily-usage': `${metrics.metrics.avgDailyUsage}h`,
        'peak-hours': metrics.metrics.peakHours,
        'most-used-app': metrics.metrics.mostUsedApp,
        'focus-ratio': metrics.metrics.focusRatio,
        'break-frequency': metrics.metrics.breakFrequency
    };
    
    Object.keys(metricElements).forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = metricElements[id];
        }
    });
}

// ========== EXPORT ==========
window.loadAnalyticsData = loadAnalyticsData;