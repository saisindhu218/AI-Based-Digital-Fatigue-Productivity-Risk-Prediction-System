// ========== DASHBOARD ROUTING & NAVIGATION ==========
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard module loaded');
    
    // Initialize all dashboard components
    initNavigation();
    initStats();
    initCharts();
    initQuickActions();
    
    // Show dashboard by default
    showSection('dashboard-home');
    
    // Check for auth
    if (!localStorage.getItem('token')) {
        window.location.href = 'login.html';
    }
});

// ========== NAVIGATION ==========
function initNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Get the target section from href
            const href = this.getAttribute('href');
            if (href.startsWith('#')) {
                const sectionId = href.substring(1);
                showSection(sectionId);
            } else if (href === 'logout') {
                // Handle logout
                if (confirm('Are you sure you want to logout?')) {
                    localStorage.clear();
                    window.location.href = 'login.html';
                }
            }
            
            // Update active nav item
            navLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
        });
    });
}

function showSection(sectionId) {
    // Hide all sections
    const sections = document.querySelectorAll('.page-section');
    sections.forEach(section => {
        section.classList.remove('active');
    });
    
    // Show target section
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.classList.add('active');
        
        // Load section-specific content
        switch(sectionId) {
            case 'analytics':
                loadAnalytics();
                break;
            case 'predictions':
                loadPredictions();
                break;
            case 'recommendations':
                loadRecommendations();
                break;
            case 'qr-pairing':
                loadQRPairing();
                break;
        }
    }
}

// ========== STATS CARDS ==========
async function initStats() {
    try {
        const stats = await fetchDashboardStats();
        updateStatsCards(stats);
    } catch (error) {
        console.error('Failed to load stats:', error);
        showNotification('Could not load dashboard statistics', 'error');
    }
}

async function fetchDashboardStats() {
    // Mock data for now - replace with actual API call
    return {
        fatigueScore: 68,
        productivityLoss: 12.5,
        screenTime: 8.2,
        sessions: 42,
        avgSession: 45,
        breaks: 16,
        fatigueLevel: 'Medium',
        weeklyChange: '+3.2'
    };
}

function updateStatsCards(stats) {
    const elements = {
        'fatigue-score': { value: `${stats.fatigueScore}%`, trend: stats.weeklyChange },
        'productivity-loss': { value: `${stats.productivityLoss}h`, trend: '-1.5h' },
        'screen-time': { value: `${stats.screenTime}h`, trend: '+0.8h' },
        'sessions': { value: stats.sessions, trend: '+5' }
    };
    
    Object.keys(elements).forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            const valueSpan = element.querySelector('.stat-value');
            const trendSpan = element.querySelector('.stat-trend');
            
            if (valueSpan) valueSpan.textContent = elements[id].value;
            if (trendSpan) {
                trendSpan.textContent = elements[id].trend;
                trendSpan.className = 'stat-trend ' + 
                    (elements[id].trest.startsWith('+') ? 'trend-up' : 'trend-down');
            }
        }
    });
}

// ========== CHARTS ==========
function initCharts() {
    // Initialize charts with mock data
    createFatigueChart();
    createProductivityChart();
    createUsageChart();
}

function createFatigueChart() {
    const ctx = document.getElementById('fatigueChart');
    if (!ctx) return;
    
    // Destroy existing chart if any
    if (window.fatigueChart) {
        window.fatigueChart.destroy();
    }
    
    const data = {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        datasets: [{
            label: 'Fatigue Level',
            data: [65, 59, 70, 71, 66, 55, 60],
            borderColor: '#667eea',
            backgroundColor: 'rgba(102, 126, 234, 0.1)',
            tension: 0.4,
            fill: true
        }]
    };
    
    window.fatigueChart = new Chart(ctx, {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
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

function createProductivityChart() {
    const ctx = document.getElementById('productivityChart');
    if (!ctx) return;
    
    if (window.productivityChart) {
        window.productivityChart.destroy();
    }
    
    const data = {
        labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
        datasets: [{
            label: 'Productivity Loss (hours)',
            data: [14, 12, 10, 8],
            backgroundColor: 'rgba(102, 126, 234, 0.8)',
            borderRadius: 10
        }]
    };
    
    window.productivityChart = new Chart(ctx, {
        type: 'bar',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
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

function createUsageChart() {
    const ctx = document.getElementById('usageChart');
    if (!ctx) return;
    
    if (window.usageChart) {
        window.usageChart.destroy();
    }
    
    const data = {
        labels: ['Work', 'Social', 'Entertainment', 'Learning', 'Other'],
        datasets: [{
            data: [35, 25, 20, 15, 5],
            backgroundColor: [
                '#667eea',
                '#764ba2',
                '#f59e0b',
                '#10b981',
                '#6b7280'
            ],
            borderWidth: 0
        }]
    };
    
    window.usageChart = new Chart(ctx, {
        type: 'doughnut',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// ========== QUICK ACTIONS ==========
function initQuickActions() {
    const actionBtns = document.querySelectorAll('.action-btn');
    
    actionBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const action = this.getAttribute('data-action');
            handleQuickAction(action);
        });
    });
}

function handleQuickAction(action) {
    switch(action) {
        case 'take-break':
            showNotification('Break reminder set for 30 minutes', 'success');
            break;
        case 'start-focus':
            showNotification('Focus mode activated for 25 minutes', 'success');
            break;
        case 'view-insights':
            showSection('analytics');
            break;
        case 'pair-device':
            showSection('qr-pairing');
            break;
        case 'set-goals':
            showNotification('Goal setting feature coming soon!', 'info');
            break;
        case 'get-recommendations':
            showSection('recommendations');
            break;
    }
}

// ========== SECTION LOADERS ==========
async function loadAnalytics() {
    // Load analytics data
    createAnalyticsCharts();
}

async function loadPredictions() {
    // Load prediction data
    try {
        const predictions = await fetchPredictions();
        updatePredictionCards(predictions);
    } catch (error) {
        console.error('Failed to load predictions:', error);
    }
}

async function loadRecommendations() {
    // Load recommendations
    updateRecommendations();
}

async function loadQRPairing() {
    // Load QR pairing
    generateQRCode();
}

// ========== HELPER FUNCTIONS ==========
function createAnalyticsCharts() {
    // This will be implemented in analytics.js
    console.log('Loading analytics charts...');
}

async function fetchPredictions() {
    // Mock data for now
    return {
        fatigueLevel: 'Medium',
        fatigueScore: 68,
        productivityLoss: 12.5,
        confidence: 82
    };
}

function updatePredictionCards(predictions) {
    const fatigueCard = document.querySelector('.fatigue-result');
    const productivityCard = document.querySelector('.productivity-result');
    
    if (fatigueCard) {
        const valueEl = fatigueCard.querySelector('.result-value');
        const labelEl = fatigueCard.querySelector('.result-label');
        
        if (valueEl) valueEl.textContent = predictions.fatigueLevel;
        if (labelEl) labelEl.textContent = `Score: ${predictions.fatigueScore}%`;
        
        // Set color based on level
        valueEl.className = 'result-value ' + 
            (predictions.fatigueLevel === 'High' ? 'fatigue-high' :
             predictions.fatigueLevel === 'Medium' ? 'fatigue-medium' : 'fatigue-low');
    }
    
    if (productivityCard) {
        const valueEl = productivityCard.querySelector('.result-value');
        const labelEl = productivityCard.querySelector('.result-label');
        
        if (valueEl) valueEl.textContent = predictions.productivityLoss;
        if (labelEl) labelEl.textContent = 'hours/week';
    }
}

function updateRecommendations() {
    // Mock recommendations
    const recommendations = [
        {
            category: 'Screen Time',
            items: [
                'Take a 5-minute break every 25 minutes',
                'Enable blue light filter after 6 PM',
                'Reduce social media usage by 30%'
            ]
        },
        {
            category: 'Sleep',
            items: [
                'Avoid screens 1 hour before bedtime',
                'Maintain consistent sleep schedule',
                'Create a dark, cool sleeping environment'
            ]
        },
        {
            category: 'Productivity',
            items: [
                'Use Pomodoro technique for focused work',
                'Schedule deep work sessions in morning',
                'Batch similar tasks together'
            ]
        }
    ];
    
    const container = document.getElementById('recommendationsContainer');
    if (!container) return;
    
    container.innerHTML = recommendations.map(rec => `
        <div class="recommendation-card">
            <div class="recomm-card-header">
                <i class="fas fa-lightbulb"></i>
                <h3>${rec.category}</h3>
            </div>
            <ul class="recomm-list">
                ${rec.items.map(item => `
                    <li>
                        <i class="fas fa-check"></i>
                        <span>${item}</span>
                    </li>
                `).join('')}
            </ul>
        </div>
    `).join('');
}

function generateQRCode() {
    const container = document.getElementById('qrcode');
    if (!container) return;
    
    // Clear previous QR code
    container.innerHTML = '';
    
    // Generate random pairing token
    const pairingToken = Math.random().toString(36).substring(2, 15);
    
    // Create QR code (using simple div for now - integrate qrcode.js if needed)
    container.innerHTML = `
        <div style="
            width: 200px; 
            height: 200px; 
            background: #f8f9fa; 
            display: flex; 
            align-items: center; 
            justify-content: center;
            border: 2px dashed #667eea;
            border-radius: 10px;
            margin: 20px auto;
        ">
            <div style="text-align: center; padding: 20px;">
                <div style="font-size: 14px; color: #666; margin-bottom: 10px;">
                    Pairing Code:
                </div>
                <div style="font-size: 24px; font-weight: bold; color: #667eea; letter-spacing: 2px;">
                    ${pairingToken.substring(0, 6)}
                </div>
                <div style="font-size: 12px; color: #999; margin-top: 10px;">
                    Scan with mobile app
                </div>
            </div>
        </div>
    `;
}

// ========== POLLING FOR UPDATES ==========
setInterval(() => {
    if (document.querySelector('.page-section.active').id === 'dashboard-home') {
        initStats();
        initCharts();
    }
}, 30000); // Update every 30 seconds