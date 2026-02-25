// ========== AUTH CHECK ==========
let authChecked = false;

document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard loaded');
    
    if (authChecked) return;
    authChecked = true;
    
    const token = localStorage.getItem('token');
    if (!token) {
        console.log("No token — redirecting to login");
        location.href = "login.html";
        return;
    }
    
    console.log('User is authenticated');
    
    // SHOW USER NAME
    const nameBox = document.getElementById("userEmail");
    const storedName = localStorage.getItem("studentName") || "User";
    if (nameBox) {
        nameBox.textContent = storedName;
    }

    initNavigation();
    initStats();
    initCharts();
    initQuickActions();
    
    showSection('dashboard-home');
    
    startStatsPolling();
});


// ========== NAVIGATION ==========
function initNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const href = this.getAttribute('href');
            if (href && href.startsWith('#')) {
                const sectionId = href.substring(1);
                showSection(sectionId);
            }
            
            navLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
        });
    });
}

function showSection(sectionId) {
    document.querySelectorAll('.page-section')
        .forEach(section => section.classList.remove('active'));

    const target = document.getElementById(sectionId);
    if (target) {
        target.classList.add('active');

        switch(sectionId) {
            case 'analytics': loadAnalytics(); break;
            case 'predictions': loadPredictions(); break;
            case 'recommendations': loadRecommendations(); break;
            case 'qr-pairing': loadQRPairing(); break;
        }
    }
}


// ========== STATS ==========
async function initStats() {
    try {
        const stats = await fetchDashboardStats();
        updateStatsCards(stats);
    } catch (err) {
        console.error(err);
        // Use default values if fetch fails
        updateStatsCards({
            fatigueScore: 0,
            productivityLoss: 0,
            screenTime: 0,
            sessions: 0
        });
    }
}

async function fetchDashboardStats() {
    // In a real app, this would fetch from API
    // For now, return mock data
    return {
        fatigueScore: Math.floor(Math.random() * 30) + 50, // 50-80
        productivityLoss: (Math.random() * 10 + 5).toFixed(1), // 5-15
        screenTime: (Math.random() * 6 + 4).toFixed(1), // 4-10
        sessions: Math.floor(Math.random() * 30) + 30 // 30-60
    };
}

function updateStatsCards(stats) {
    const fatigueEl = document.getElementById('fatigue-score');
    if (fatigueEl) fatigueEl.textContent = `${stats.fatigueScore}%`;
    
    const productivityEl = document.getElementById('productivity-loss');
    if (productivityEl) productivityEl.textContent = `${stats.productivityLoss}h`;
    
    const screenTimeEl = document.getElementById('screen-time');
    if (screenTimeEl) screenTimeEl.textContent = `${stats.screenTime}h`;
    
    const sessionsEl = document.getElementById('sessions');
    if (sessionsEl) sessionsEl.textContent = stats.sessions;
}


// ========== CHARTS ==========
function initCharts() {
    createFatigueChart();
    createProductivityChart();
    createUsageChart();
}


function createFatigueChart() {
    const ctx = document.getElementById('fatigueChart');
    if (!ctx) return;

    if (window.fatigueChart instanceof Chart) {
        window.fatigueChart.destroy();
    }

    window.fatigueChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'Fatigue Level',
                data: [65, 59, 70, 71, 66, 55, 60],
                borderColor: '#667eea',
                backgroundColor: 'rgba(102,126,234,0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            }
        }
    });
}


function createProductivityChart() {
    const ctx = document.getElementById('productivityChart');
    if (!ctx) return;

    if (window.productivityChart instanceof Chart) {
        window.productivityChart.destroy();
    }

    window.productivityChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Week1', 'Week2', 'Week3', 'Week4'],
            datasets: [{
                label: 'Hours Lost',
                data: [14, 12, 10, 8],
                backgroundColor: 'rgba(102,126,234,0.8)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            }
        }
    });
}


function createUsageChart() {
    const ctx = document.getElementById('usageChart');
    if (!ctx) return;

    if (window.usageChart instanceof Chart) {
        window.usageChart.destroy();
    }

    window.usageChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Work', 'Social', 'Entertainment', 'Learning', 'Other'],
            datasets: [{
                data: [35, 25, 20, 15, 5],
                backgroundColor: [
                    '#667eea', '#764ba2', '#f59e0b', '#10b981', '#6b7280'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });
}


// ========== QUICK ACTIONS ==========
function initQuickActions() {
    document.querySelectorAll('.action-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            handleQuickAction(btn.dataset.action);
        });
    });
}

function handleQuickAction(action) {
    switch(action) {
        case 'view-insights': 
            showSection('analytics'); 
            break;
        case 'pair-device': 
            showSection('qr-pairing'); 
            break;
        default: 
            alert("Action: " + action);
    }
}


// ========== LOADERS ==========
async function loadAnalytics() { 
    console.log("analytics load"); 
}

async function loadPredictions() { 
    console.log("predictions load"); 
}

async function loadRecommendations() { 
    console.log("recommendations load"); 
}

async function loadQRPairing() { 
    generateQRCode(); 
}


// ========== QR ==========
function generateQRCode() {
    const box = document.getElementById('qrcode');
    if (!box) return;

    const code = Math.random().toString(36).substring(2, 8).toUpperCase();

    box.innerHTML = `
        <div style="padding:30px;border:2px dashed #667eea;text-align:center">
            <h2>${code}</h2>
            <small>Scan with mobile</small>
        </div>`;
    
    // Update the pairing code display
    const codeEl = document.querySelector('.pairing-code strong');
    if (codeEl) codeEl.textContent = code;
}


// ========== POLLING ==========
let statsInterval;
function startStatsPolling() {
    if (statsInterval) clearInterval(statsInterval);

    statsInterval = setInterval(() => {
        const active = document.querySelector('.page-section.active');
        if (active && active.id === "dashboard-home") {
            initStats();
        }
    }, 120000); // 2 minutes
}