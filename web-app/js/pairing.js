// ========== QR PAIRING ==========

document.addEventListener('DOMContentLoaded', function () {
    console.log('Pairing module loaded');

    const pairingSection = document.getElementById('qr-pairing');
    if (!pairingSection) return;

    // Prevent duplicate observers
    if (window.pairingObserverAttached) return;
    window.pairingObserverAttached = true;

    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                const section = mutation.target;

                if (section.id === 'qr-pairing' && section.classList.contains('active')) {
                    if (!window.pairingInitialized) {
                        window.pairingInitialized = true;
                        initializePairing();
                    }
                }
            }
        });
    });

    observer.observe(pairingSection, { attributes: true });
});


// ========== INITIALIZER ==========
function initializePairing() {
    console.log('Initializing pairing...');

    generateQRCode();
    setupRefreshButton();
    startDeviceStatusPolling();
}


// ========== REFRESH BUTTON ==========
function setupRefreshButton() {
    const refreshBtn = document.getElementById('refreshQR');
    if (!refreshBtn) return;

    // prevent multiple listeners
    if (refreshBtn.dataset.listenerAttached) return;
    refreshBtn.dataset.listenerAttached = true;

    refreshBtn.addEventListener('click', generateQRCode);
}


// ========== QR GENERATOR ==========
function generateQRCode() {
    const container = document.getElementById('qrcode');
    if (!container) return;

    container.innerHTML = '';

    const pairingToken = Math.random().toString(36).substring(2, 15).toUpperCase();

    container.innerHTML = `
        <div style="
            width:200px;
            height:200px;
            background:#f8f9fa;
            display:flex;
            align-items:center;
            justify-content:center;
            border:2px dashed #667eea;
            border-radius:10px;
            margin:20px auto;
        ">
            <div style="text-align:center;padding:20px;">
                <div style="font-size:14px;color:#666;margin-bottom:10px;">
                    Pairing Code:
                </div>
                <div style="font-size:24px;font-weight:bold;color:#667eea;letter-spacing:2px;">
                    ${pairingToken}
                </div>
                <div style="font-size:12px;color:#999;margin-top:10px;">
                    Scan with mobile app
                </div>
            </div>
        </div>
    `;

    localStorage.setItem('pairingToken', pairingToken);
    localStorage.setItem('pairingExpiry', Date.now() + (10 * 60 * 1000));

    console.log('Generated pairing code:', pairingToken);
}


// ========== POLLING ==========
let pairingInterval = null;

function startDeviceStatusPolling() {

    if (pairingInterval) return; // prevent duplicates

    checkDeviceStatus();

    pairingInterval = setInterval(checkDeviceStatus, 10000);
}


// ========== STATUS CHECK ==========
async function checkDeviceStatus() {
    try {
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


// ========== STATUS UI ==========
function updateDeviceStatusUI(status) {

    const laptopStatus = document.querySelectorAll('.status-item')[0]?.children[1];
    const mobileStatus = document.querySelectorAll('.status-item')[1]?.children[1];
    const lastSynced = document.querySelectorAll('.status-item')[2]?.children[1];
    const dataPoints = document.querySelectorAll('.status-item')[3]?.children[1];

    if (laptopStatus) {
        laptopStatus.innerHTML =
            status.laptop === 'connected'
                ? '<i class="fas fa-check-circle"></i> Connected'
                : '<i class="fas fa-times-circle"></i> Disconnected';

        laptopStatus.className =
            status.laptop === 'connected'
                ? 'status-connected'
                : 'status-disconnected';
    }

    if (mobileStatus) {
        mobileStatus.innerHTML =
            status.mobile === 'connected'
                ? '<i class="fas fa-check-circle"></i> Connected'
                : '<i class="fas fa-times-circle"></i> Not Connected';

        mobileStatus.className =
            status.mobile === 'connected'
                ? 'status-connected'
                : 'status-disconnected';
    }

    if (lastSynced) lastSynced.textContent = status.lastSynced;
    if (dataPoints) dataPoints.textContent = status.dataPoints.toLocaleString();
}


// ========== MOCK MOBILE CONNECT ==========
function simulateMobileConnection() {
    const token = prompt('Enter pairing code from mobile app:');
    const storedToken = localStorage.getItem('pairingToken');

    if (token === storedToken) {
        alert('Mobile device connected successfully!');
        updateDeviceStatusUI({
            mobile: 'connected',
            lastSynced: new Date().toLocaleTimeString()
        });
    } else {
        alert('Invalid pairing code');
    }
}

window.simulateMobileConnection = simulateMobileConnection;