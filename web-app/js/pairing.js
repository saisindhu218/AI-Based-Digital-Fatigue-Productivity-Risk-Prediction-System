// ========== QR PAIRING ==========
document.addEventListener('DOMContentLoaded', function() {
    console.log('Pairing module loaded');
    
    // Only run on pairing page
    if (!document.getElementById('qr-pairing')) return;
    
    initPairing();
});

function initPairing() {
    const refreshBtn = document.getElementById('refreshQR');
    
    if (refreshBtn) {
        refreshBtn.addEventListener('click', generateNewQRCode);
    }
    
    // Generate initial QR code
    generateQRCode();
    
    // Start checking device status
    startDeviceStatusPolling();
}

function generateNewQRCode() {
    const container = document.getElementById('qrcode');
    if (!container) return;
    
    // Show loading
    const oldContent = container.innerHTML;
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
            <div style="text-align: center;">
                <i class="fas fa-spinner fa-spin" style="font-size: 30px; color: #667eea;"></i>
                <div style="margin-top: 10px; font-size: 14px; color: #666;">
                    Generating...
                </div>
            </div>
        </div>
    `;
    
    // Simulate API call
    setTimeout(() => {
        generateQRCode();
        showNotification('New pairing code generated', 'success');
    }, 1000);
}

function generateQRCode() {
    const container = document.getElementById('qrcode');
    if (!container) return;
    
    // Generate random pairing token
    const token = generateToken();
    
    // Create QR code using canvas (simple version)
    container.innerHTML = `
        <div style="
            width: 200px; 
            height: 200px; 
            background: #f8f9fa; 
            display: flex; 
            align-items: center; 
            justify-content: center;
            border: 2px solid #667eea;
            border-radius: 10px;
            margin: 20px auto;
            position: relative;
            overflow: hidden;
        ">
            <!-- QR pattern simulation -->
            <div style="
                position: absolute;
                top: 20px;
                left: 20px;
                right: 20px;
                bottom: 20px;
                display: grid;
                grid-template-columns: repeat(7, 1fr);
                grid-template-rows: repeat(7, 1fr);
                gap: 2px;
            ">
                ${Array(49).fill(0).map((_, i) => `
                    <div style="
                        background: ${Math.random() > 0.5 ? '#667eea' : 'transparent'};
                        border-radius: 2px;
                    "></div>
                `).join('')}
            </div>
            
            <!-- Center logo -->
            <div style="
                width: 40px;
                height: 40px;
                background: white;
                border: 3px solid #667eea;
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 1;
            ">
                <i class="fas fa-brain" style="color: #667eea;"></i>
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 15px;">
            <div style="font-size: 14px; color: #666;">
                Pairing Code:
            </div>
            <div style="
                font-size: 24px; 
                font-weight: bold; 
                color: #667eea; 
                letter-spacing: 3px;
                margin: 10px 0;
            ">
                ${token}
            </div>
            <div style="font-size: 12px; color: #999;">
                Valid for 10 minutes
            </div>
        </div>
    `;
    
    // Store token for verification
    localStorage.setItem('pairingToken', token);
    localStorage.setItem('pairingExpiry', Date.now() + (10 * 60 * 1000));
}

function generateToken() {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    let token = '';
    for (let i = 0; i < 8; i++) {
        token += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return token;
}

async function startDeviceStatusPolling() {
    // Initial check
    await checkDeviceStatus();
    
    // Poll every 10 seconds
    setInterval(checkDeviceStatus, 10000);
}

async function checkDeviceStatus() {
    try {
        // Mock API call - replace with actual
        const status = {
            laptop: 'connected',
            mobile: Math.random() > 0.5 ? 'connected' : 'disconnected',
            lastSynced: new Date(Date.now() - Math.random() * 60000).toLocaleTimeString(),
            dataPoints: Math.floor(1247 + Math.random() * 100)
        };
        
        updateDeviceStatusUI(status);
    } catch (error) {
        console.error('Failed to check device status:', error);
    }
}

function updateDeviceStatusUI(status) {
    const elements = {
        laptop: document.querySelector('.status-item:nth-child(1) .status-connected'),
        mobile: document.querySelector('.status-item:nth-child(2) .status-disconnected'),
        lastSynced: document.querySelector('.status-item:nth-child(3) span:last-child'),
        dataPoints: document.querySelector('.status-item:nth-child(4) span:last-child')
    };
    
    if (elements.laptop) {
        elements.laptop.innerHTML = status.laptop === 'connected' 
            ? '<i class="fas fa-check-circle"></i> Connected'
            : '<i class="fas fa-times-circle"></i> Disconnected';
        elements.laptop.className = status.laptop === 'connected' 
            ? 'status-connected' 
            : 'status-disconnected';
    }
    
    if (elements.mobile) {
        elements.mobile.innerHTML = status.mobile === 'connected' 
            ? '<i class="fas fa-check-circle"></i> Connected'
            : '<i class="fas fa-times-circle"></i> Not Connected';
        elements.mobile.className = status.mobile === 'connected' 
            ? 'status-connected' 
            : 'status-disconnected';
    }
    
    if (elements.lastSynced) {
        elements.lastSynced.textContent = status.lastSynced;
    }
    
    if (elements.dataPoints) {
        elements.dataPoints.textContent = status.dataPoints.toLocaleString();
    }
}

// ========== MOCK DEVICE CONNECTION ==========
// For testing without mobile app
function simulateMobileConnection() {
    const token = prompt('Enter pairing code from mobile app:');
    const storedToken = localStorage.getItem('pairingToken');
    
    if (token === storedToken) {
        showNotification('Mobile device connected successfully!', 'success');
        
        // Update status
        const status = {
            mobile: 'connected',
            lastSynced: new Date().toLocaleTimeString()
        };
        
        updateDeviceStatusUI(status);
    } else {
        showNotification('Invalid pairing code', 'error');
    }
}

// Add to window for testing
window.simulateMobileConnection = simulateMobileConnection;