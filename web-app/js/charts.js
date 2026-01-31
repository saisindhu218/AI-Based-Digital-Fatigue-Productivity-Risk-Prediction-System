// Chart initialization and management
class ChartManager {
    constructor() {
        this.charts = new Map();
        this.initCharts();
    }

    initCharts() {
        this.initFatigueChart();
        this.initAppUsageChart();
        this.initScreenTimeChart();
    }

    initFatigueChart() {
        const ctx = document.getElementById('fatigue-chart');
        if (!ctx) return;

        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Fatigue Score',
                    data: [45, 52, 68, 74, 62, 55, 48],
                    borderColor: '#4A90E2',
                    backgroundColor: 'rgba(74, 144, 226, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
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
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            label: function(context) {
                                return `Fatigue: ${context.parsed.y}%`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    }
                }
            }
        });

        this.charts.set('fatigue', chart);
    }

    initAppUsageChart() {
        const ctx = document.getElementById('app-usage-chart');
        if (!ctx) return;

        const chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['VS Code', 'Chrome', 'Slack', 'Terminal', 'Other'],
                datasets: [{
                    data: [35, 25, 20, 10, 10],
                    backgroundColor: [
                        '#4A90E2',
                        '#50C878',
                        '#7B68EE',
                        '#FFA500',
                        '#95A5A6'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            pointStyle: 'circle'
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = Math.round((value / total) * 100);
                                return `${label}: ${percentage}% (${value} mins)`;
                            }
                        }
                    }
                },
                cutout: '65%'
            }
        });

        this.charts.set('app-usage', chart);
    }

    initScreenTimeChart() {
        const ctx = document.getElementById('screen-time-chart');
        if (!ctx) return;

        // Generate time labels for last 7 days
        const days = [];
        for (let i = 6; i >= 0; i--) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            days.push(date.toLocaleDateString('en-US', { weekday: 'short' }));
        }

        const chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: days,
                datasets: [
                    {
                        label: 'Laptop',
                        data: [4.2, 5.1, 3.8, 6.2, 4.5, 2.1, 1.8],
                        backgroundColor: '#4A90E2',
                        borderRadius: 6
                    },
                    {
                        label: 'Mobile',
                        data: [3.1, 2.8, 4.2, 2.5, 3.8, 4.2, 3.5],
                        backgroundColor: '#7B68EE',
                        borderRadius: 6
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            label: function(context) {
                                return `${context.dataset.label}: ${context.parsed.y} hours`;
                            },
                            footer: function(tooltipItems) {
                                const total = tooltipItems.reduce((sum, item) => sum + item.parsed.y, 0);
                                return `Total: ${total.toFixed(1)} hours`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Hours'
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
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

        this.charts.set('screen-time', chart);
    }

    updateFatigueChart(data) {
        const chart = this.charts.get('fatigue');
        if (chart && data) {
            chart.data.datasets[0].data = data;
            chart.update();
        }
    }

    updateAppUsageChart(data) {
        const chart = this.charts.get('app-usage');
        if (chart && data) {
            chart.data.labels = data.labels;
            chart.data.datasets[0].data = data.values;
            chart.update();
        }
    }

    updateScreenTimeChart(data) {
        const chart = this.charts.get('screen-time');
        if (chart && data) {
            chart.data.datasets[0].data = data.laptop;
            chart.data.datasets[1].data = data.mobile;
            chart.update();
        }
    }

    destroyAll() {
        this.charts.forEach(chart => chart.destroy());
        this.charts.clear();
    }
}

// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.chartManager = new ChartManager();
    
    // Update charts with real data from API
    updateChartsWithRealData();
});

async function updateChartsWithRealData() {
    try {
        const authManager = window.authManager;
        if (!authManager || !authManager.isAuthenticated()) return;

        // Fetch real data from API
        const response = await fetch('http://localhost:8000/api/v1/usage/user/current/recent?hours=168', {
            headers: authManager.getAuthHeaders()
        });

        if (response.ok) {
            const usageData = await response.json();
            
            // Process and update charts with real data
            if (window.chartManager) {
                // Update fatigue chart with historical data
                const fatigueData = processFatigueData(usageData);
                window.chartManager.updateFatigueChart(fatigueData);
                
                // Update app usage chart
                const appUsageData = processAppUsageData(usageData);
                window.chartManager.updateAppUsageChart(appUsageData);
                
                // Update screen time chart
                const screenTimeData = processScreenTimeData(usageData);
                window.chartManager.updateScreenTimeChart(screenTimeData);
            }
        }
    } catch (error) {
        console.error('Error updating charts:', error);
    }
}

function processFatigueData(usageData) {
    // Process usage data to generate fatigue scores
    // This would typically come from prediction history
    // For now, return mock data
    return [45, 52, 68, 74, 62, 55, 48];
}

function processAppUsageData(usageData) {
    // Aggregate app usage from laptop and mobile data
    const appUsage = {};
    
    // Process laptop apps
    if (usageData.laptop_usage) {
        usageData.laptop_usage.forEach(entry => {
            const app = entry.active_app || 'Unknown';
            appUsage[app] = (appUsage[app] || 0) + (entry.usage_duration || 0);
        });
    }
    
    // Process mobile apps
    if (usageData.mobile_usage) {
        usageData.mobile_usage.forEach(entry => {
            const app = entry.app_name || 'Unknown';
            appUsage[app] = (appUsage[app] || 0) + (entry.screen_time || 0);
        });
    }
    
    // Get top 5 apps
    const sortedApps = Object.entries(appUsage)
        .sort(([, a], [, b]) => b - a)
        .slice(0, 5);
    
    return {
        labels: sortedApps.map(([app]) => app),
        values: sortedApps.map(([, duration]) => Math.round(duration))
    };
}

function processScreenTimeData(usageData) {
    // Aggregate screen time by day
    const laptopByDay = Array(7).fill(0);
    const mobileByDay = Array(7).fill(0);
    
    // Process data (simplified - in real app, group by day)
    if (usageData.totals) {
        const dailyAvg = usageData.totals.total_screen_time / 7 / 60; // Convert to hours
        laptopByDay.fill(dailyAvg * 0.6); // 60% laptop
        mobileByDay.fill(dailyAvg * 0.4); // 40% mobile
    }
    
    return {
        laptop: laptopByDay.map(hours => parseFloat(hours.toFixed(1))),
        mobile: mobileByDay.map(hours => parseFloat(hours.toFixed(1)))
    };
}

// Export for module usage if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ChartManager };
}