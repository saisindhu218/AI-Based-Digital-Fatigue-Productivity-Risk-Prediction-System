// Dashboard functionality
class Dashboard {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000/api/v1';
        this.userId = localStorage.getItem('userId');
        this.token = localStorage.getItem('authToken');
        
        this.init();
    }
    
    init() {
        this.setupNavigation();
        this.loadDashboardData();
        this.setupEventListeners();
        this.updateLiveData();
    }
    
    setupNavigation() {
        const navLinks = document.querySelectorAll('.nav-link');
        const sections = document.querySelectorAll('.section');
        
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = link.getAttribute('href').substring(1);
                
                // Update active nav link
                navLinks.forEach(l => l.classList.remove('active'));
                link.classList.add('active');
                
                // Show target section
                sections.forEach(section => {
                    section.classList.remove('active');
                    if (section.id === targetId) {
                        section.classList.add('active');
                    }
                });
                
                // Load section-specific data
                this.loadSectionData(targetId);
            });
        });
    }
    
    async loadDashboardData() {
        if (!this.userId || !this.token) {
            window.location.href = 'login.html';
            return;
        }
        
        try {
            // Load fatigue prediction
            const prediction = await this.fetchPrediction();
            this.updateFatigueDisplay(prediction);
            
            // Load usage data
            const usageData = await this.fetchUsageData();
            this.updateUsageDisplay(usageData);
            
            // Load device status
            const devices = await this.fetchDeviceStatus();
            this.updateDeviceStatus(devices);
            
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            this.showError('Failed to load dashboard data');
        }
    }
    
    async fetchPrediction() {
        const response = await fetch(`${this.apiBaseUrl}/prediction/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.token}`
            },
            body: JSON.stringify({
                user_id: this.userId,
                timestamp: new Date().toISOString(),
                features: {}
            })
        });
        
        if (!response.ok) throw new Error('Failed to fetch prediction');
        return await response.json();
    }
    
    async fetchUsageData(hours = 24) {
        const response = await fetch(
            `${this.apiBaseUrl}/usage/user/${this.userId}/recent?hours=${hours}`,
            {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            }
        );
        
        if (!response.ok) throw new Error('Failed to fetch usage data');
        return await response.json();
    }
    
    async fetchDeviceStatus() {
        // In production, implement actual device status check
        return {
            laptop: { connected: true, lastActive: '2 minutes ago' },
            mobile: { connected: true, lastActive: '5 minutes ago' }
        };
    }
    
    updateFatigueDisplay(prediction) {
        document.getElementById('fatigue-score').textContent = 
            Math.round(prediction.fatigue_score);
        
        document.getElementById('productivity-loss').textContent = 
            prediction.productivity_loss.toFixed(1);
        
        // Update fatigue level indicator
        const fatigueLevel = prediction.fatigue_level;
        const fatigueCard = document.querySelector('.stat-card.primary');
        
        fatigueCard.querySelector('.stat-label').textContent = `${fatigueLevel} Risk`;
        
        // Update progress bar
        const progressFill = fatigueCard.querySelector('.progress-fill');
        progressFill.style.width = `${prediction.fatigue_score}%`;
        
        // Color code based on level
        if (fatigueLevel === 'High') {
            progressFill.style.backgroundColor = 'var(--danger-color)';
        } else if (fatigueLevel === 'Medium') {
            progressFill.style.backgroundColor = 'var(--warning-color)';
        } else {
            progressFill.style.backgroundColor = 'var(--success-color)';
        }
    }
    
    updateUsageDisplay(usageData) {
        const totals = usageData.totals;
        
        // Convert minutes to hours
        const laptopHours = (totals.laptop_minutes / 60).toFixed(1);
        const mobileHours = (totals.mobile_minutes / 60).toFixed(1);
        const totalHours = (totals.total_screen_time / 60).toFixed(1);
        
        document.getElementById('laptop-usage').textContent = laptopHours;
        document.getElementById('mobile-usage').textContent = mobileHours;
        
        // Update progress bars
        const laptopCard = document.querySelector('.stat-card.success .progress-fill');
        const mobileCard = document.querySelector('.stat-card.info .progress-fill');
        
        // Calculate percentages (assuming 10 hours max for visualization)
        laptopCard.style.width = `${Math.min((laptopHours / 10) * 100, 100)}%`;
        mobileCard.style.width = `${Math.min((mobileHours / 10) * 100, 100)}%`;
    }
    
    updateDeviceStatus(devices) {
        const laptopStatus = document.querySelector('.status-badge:nth-child(1)');
        const mobileStatus = document.querySelector('.status-badge:nth-child(2)');
        
        if (devices.laptop.connected) {
            laptopStatus.innerHTML = '<i class="fas fa-laptop"></i> Laptop: Connected';
            laptopStatus.className = 'status-badge connected';
        } else {
            laptopStatus.innerHTML = '<i class="fas fa-laptop"></i> Laptop: Disconnected';
            laptopStatus.className = 'status-badge disconnected';
        }
        
        if (devices.mobile.connected) {
            mobileStatus.innerHTML = '<i class="fas fa-mobile-alt"></i> Mobile: Connected';
            mobileStatus.className = 'status-badge connected';
        } else {
            mobileStatus.innerHTML = '<i class="fas fa-mobile-alt"></i> Mobile: Disconnected';
            mobileStatus.className = 'status-badge disconnected';
        }
    }
    
    setupEventListeners() {
        // QR code refresh
        const refreshBtn = document.getElementById('refresh-qr');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshQRCode());
        }
        
        // Time range filter
        const timeRange = document.getElementById('time-range');
        if (timeRange) {
            timeRange.addEventListener('change', (e) => {
                this.loadUsageData(parseInt(e.target.value));
            });
        }
    }
    
    async refreshQRCode() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/pairing/generate-qr`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify({
                    device_id: `laptop_${this.generateDeviceId()}`,
                    device_type: 'laptop',
                    device_name: 'My Laptop',
                    user_id: this.userId
                })
            });
            
            if (!response.ok) throw new Error('Failed to generate QR code');
            
            const qrData = await response.json();
            document.getElementById('qr-code-img').src = qrData.qr_code_url;
            
            this.showNotification('QR code refreshed successfully', 'success');
            
        } catch (error) {
            console.error('Error refreshing QR code:', error);
            this.showNotification('Failed to refresh QR code', 'error');
        }
    }
    
    generateDeviceId() {
        return Math.random().toString(36).substring(2, 10);
    }
    
    updateLiveData() {
        // Update data every 60 seconds
        setInterval(() => {
            this.loadDashboardData();
        }, 60000);
    }
    
    loadSectionData(sectionId) {
        switch(sectionId) {
            case 'analytics':
                this.loadAnalyticsData();
                break;
            case 'predictions':
                this.loadPredictionsHistory();
                break;
            case 'notifications':
                this.loadNotifications();
                break;
        }
    }
    
    async loadAnalyticsData() {
        try {
            const usageData = await this.fetchUsageData(168); // Last 7 days
            // Update charts with usageData
            this.updateAnalyticsCharts(usageData);
            
        } catch (error) {
            console.error('Error loading analytics:', error);
        }
    }
    
    updateAnalyticsCharts(usageData) {
        // Implement chart updates based on usageData
        console.log('Updating analytics charts with:', usageData);
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
            <span>${message}</span>
            <button class="notification-close"><i class="fas fa-times"></i></button>
        `;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
        
        // Close button
        notification.querySelector('.notification-close').addEventListener('click', () => {
            notification.remove();
        });
    }
    
    showError(message) {
        this.showNotification(message, 'error');
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new Dashboard();
});