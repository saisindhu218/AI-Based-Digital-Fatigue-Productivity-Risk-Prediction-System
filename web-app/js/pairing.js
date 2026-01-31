// Device Pairing Module
class PairingManager {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000/api/v1';
        this.authManager = window.authManager;
        this.currentQRCode = null;
    }

    async generateQRCode() {
        try {
            if (!this.authManager || !this.authManager.isAuthenticated()) {
                throw new Error('Not authenticated');
            }

            const user = this.authManager.getCurrentUser();
            const deviceId = `laptop_${this.generateDeviceId()}`;

            const response = await fetch(`${this.apiBaseUrl}/pairing/generate-qr`, {
                method: 'POST',
                headers: this.authManager.getAuthHeaders(),
                body: JSON.stringify({
                    device_id: deviceId,
                    device_type: 'laptop',
                    device_name: 'My Laptop',
                    user_id: user.userId || user.email
                })
            });

            if (!response.ok) {
                throw new Error('Failed to generate QR code');
            }

            const qrData = await response.json();
            this.currentQRCode = qrData;
            
            // Update QR code display
            this.updateQRDisplay(qrData.qr_code_url);
            
            // Start checking pairing status
            this.startPairingPolling(qrData.token);
            
            return qrData;
            
        } catch (error) {
            console.error('Error generating QR code:', error);
            this.showError('Failed to generate QR code: ' + error.message);
            return null;
        }
    }

    updateQRDisplay(qrCodeUrl) {
        const qrImg = document.getElementById('qr-code-img');
        if (qrImg) {
            qrImg.src = qrCodeUrl;
        }
        
        const qrContainer = document.querySelector('.qr-container');
        if (qrContainer) {
            qrContainer.innerHTML = `
                <img src="${qrCodeUrl}" alt="QR Code">
                <div class="qr-instructions">
                    <h4>Scan with Mobile App</h4>
                    <p>1. Open FatigueGuard mobile app</p>
                    <p>2. Tap on "Scan QR Code"</p>
                    <p>3. Point camera at this code</p>
                    <p class="qr-expiry">QR expires in 5 minutes</p>
                </div>
            `;
        }
    }

    startPairingPolling(token) {
        // Poll for pairing status every 5 seconds
        let attempts = 0;
        const maxAttempts = 60; // 5 minutes
        
        const poll = async () => {
            if (attempts >= maxAttempts) {
                this.showError('QR code expired. Please generate a new one.');
                return;
            }
            
            attempts++;
            
            try {
                const isPaired = await this.checkPairingStatus(token);
                if (isPaired) {
                    this.showSuccess('Device paired successfully!');
                    this.updateDeviceStatus(true);
                    return;
                }
                
                // Continue polling
                setTimeout(poll, 5000);
                
            } catch (error) {
                console.error('Error checking pairing status:', error);
                setTimeout(poll, 5000);
            }
        };
        
        poll();
    }

    async checkPairingStatus(token) {
        // This endpoint would need to be implemented in the backend
        // For now, we'll simulate checking
        return false;
    }

    generateDeviceId() {
        // Generate a unique device ID
        return Math.random().toString(36).substring(2, 15) + 
               Math.random().toString(36).substring(2, 15);
    }

    async getPairedDevices() {
        try {
            if (!this.authManager || !this.authManager.isAuthenticated()) {
                return [];
            }

            const response = await fetch(`${this.apiBaseUrl}/pairing/devices`, {
                headers: this.authManager.getAuthHeaders()
            });

            if (response.ok) {
                const devices = await response.json();
                return devices;
            }
            
            return [];
            
        } catch (error) {
            console.error('Error fetching paired devices:', error);
            return [];
        }
    }

    async unpairDevice(deviceId) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/pairing/unpair`, {
                method: 'POST',
                headers: this.authManager.getAuthHeaders(),
                body: JSON.stringify({ device_id: deviceId })
            });

            if (!response.ok) {
                throw new Error('Failed to unpair device');
            }

            this.showSuccess('Device unpaired successfully');
            return true;
            
        } catch (error) {
            console.error('Error unpairing device:', error);
            this.showError('Failed to unpair device: ' + error.message);
            return false;
        }
    }

    updateDeviceStatus(isPaired) {
        const statusElement = document.querySelector('.pairing-status');
        if (statusElement) {
            if (isPaired) {
                statusElement.innerHTML = `
                    <i class="fas fa-check-circle connected"></i>
                    <span>Device paired successfully!</span>
                `;
                statusElement.className = 'pairing-status connected';
            } else {
                statusElement.innerHTML = `
                    <i class="fas fa-clock"></i>
                    <span>Waiting for mobile device...</span>
                `;
                statusElement.className = 'pairing-status waiting';
            }
        }
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `pairing-notification ${type}`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
            <span>${message}</span>
            <button class="notification-close"><i class="fas fa-times"></i></button>
        `;
        
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

    // Initialize pairing module
    init() {
        // Add refresh QR button event listener
        const refreshBtn = document.getElementById('refresh-qr');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', async (e) => {
                e.preventDefault();
                refreshBtn.disabled = true;
                refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
                
                await this.generateQRCode();
                
                refreshBtn.disabled = false;
                refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i> Refresh QR Code';
            });
        }
        
        // Load existing QR code if any
        this.loadExistingQRCode();
    }

    async loadExistingQRCode() {
        // Check if there's an existing unpaired QR code
        // This would be implemented with backend storage
        const existingQR = await this.getCurrentQRCode();
        if (existingQR) {
            this.currentQRCode = existingQR;
            this.updateQRDisplay(existingQR.qr_code_url);
            this.startPairingPolling(existingQR.token);
        }
    }

    async getCurrentQRCode() {
        // This would fetch the current active QR code from backend
        // For now, return null
        return null;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.pairingManager = new PairingManager();
    
    // If we're on a page with QR functionality, initialize it
    if (document.querySelector('.pairing-section')) {
        window.pairingManager.init();
        
        // Auto-generate QR code on page load
        setTimeout(() => {
            window.pairingManager.generateQRCode();
        }, 1000);
    }
});