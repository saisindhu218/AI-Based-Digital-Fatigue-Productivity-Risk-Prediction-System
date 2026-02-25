// ========== GLOBAL VARIABLES ==========
const API_BASE_URL = 'http://localhost:8000';
let authToken = localStorage.getItem('token');
let currentUser = JSON.parse(localStorage.getItem('user') || '{}');

// ========== DOM ELEMENTS ==========
let loginForm, registerForm, logoutBtn;

// ========== INITIALIZE ==========
document.addEventListener('DOMContentLoaded', function() {
    console.log('Auth module loaded');
    
    // Check which page we're on
    if (document.getElementById('loginForm')) {
        setupLogin();
    } else if (document.getElementById('registerForm')) {
        setupRegister();
    } else if (document.getElementById('logoutBtn')) {
        setupDashboard();
    }
    
    // Check authentication status
    checkAuth();
});

// ========== AUTH FUNCTIONS ==========
function checkAuth() {
    const publicPages = ['/', '/index.html', '/login.html', '/register.html'];
    const currentPath = window.location.pathname;
    
    if (authToken && publicPages.some(page => currentPath.endsWith(page))) {
        // Already logged in, redirect to dashboard
        window.location.href = 'index.html';
        return;
    }
    
    if (!authToken && !publicPages.some(page => currentPath.endsWith(page))) {
        // Not logged in, redirect to login
        window.location.href = 'login.html';
        return;
    }
}

// ========== LOGIN SETUP ==========
function setupLogin() {
    loginForm = document.getElementById('loginForm');
    
    if (!loginForm) return;
    
    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        
        // Show loading
        const submitBtn = loginForm.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Logging in...';
        submitBtn.disabled = true;
        
        try {
            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: email,
                    password: password
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Save token and user data
                localStorage.setItem('token', data.access_token);
                localStorage.setItem('user', JSON.stringify(data.user));
                localStorage.setItem('token_expiry', Date.now() + (30 * 60 * 1000)); // 30 minutes
                
                // Show success message
                showNotification('Login successful! Redirecting...', 'success');
                
                // Redirect to dashboard after delay
                setTimeout(() => {
                    window.location.href = 'index.html';
                }, 1500);
            } else {
                throw new Error(data.detail || 'Login failed');
            }
        } catch (error) {
            console.error('Login error:', error);
            showNotification(error.message, 'error');
        } finally {
            // Reset button
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        }
    });
    
    // Login as test user button
    const testLoginBtn = document.getElementById('testLoginBtn');
    if (testLoginBtn) {
        testLoginBtn.addEventListener('click', function() {
            document.getElementById('email').value = 'test@fatigueguard.com';
            document.getElementById('password').value = 'password123';
            loginForm.dispatchEvent(new Event('submit'));
        });
    }
}

// ========== REGISTER SETUP ==========
function setupRegister() {
    registerForm = document.getElementById('registerForm');
    
    if (!registerForm) return;
    
    registerForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const name = document.getElementById('name').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        const role = document.getElementById('role').value;
        
        // Validation
        if (password !== confirmPassword) {
            showNotification('Passwords do not match!', 'error');
            return;
        }
        
        if (password.length < 6) {
            showNotification('Password must be at least 6 characters', 'error');
            return;
        }
        
        // Show loading
        const submitBtn = registerForm.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Creating account...';
        submitBtn.disabled = true;
        
        try {
            const response = await fetch(`${API_BASE_URL}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name: name,
                    email: email,
                    password: password,
                    role: role
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                showNotification('Registration successful! Please login.', 'success');
                
                // Redirect to login after delay
                setTimeout(() => {
                    window.location.href = 'login.html';
                }, 2000);
            } else {
                throw new Error(data.detail || 'Registration failed');
            }
        } catch (error) {
            console.error('Registration error:', error);
            showNotification(error.message, 'error');
        } finally {
            // Reset button
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        }
    });
}

// ========== DASHBOARD SETUP ==========
function setupDashboard() {
    logoutBtn = document.getElementById('logoutBtn');
    const userEmail = document.getElementById('userEmail');
    
    // Update user email if element exists
    if (userEmail && currentUser.email) {
        userEmail.textContent = currentUser.email;
    }
    
    // Setup logout
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function() {
            if (confirm('Are you sure you want to logout?')) {
                localStorage.clear();
                window.location.href = 'login.html';
            }
        });
    }
    
    // Check token expiry every minute
    setInterval(checkTokenExpiry, 60000);
}

// ========== TOKEN MANAGEMENT ==========
function checkTokenExpiry() {
    const expiry = localStorage.getItem('token_expiry');
    if (expiry && Date.now() > parseInt(expiry)) {
        showNotification('Your session has expired. Please login again.', 'warning');
        setTimeout(() => {
            localStorage.clear();
            window.location.href = 'login.html';
        }, 3000);
    }
}

// ========== API HELPER ==========
async function apiRequest(endpoint, options = {}) {
    const token = localStorage.getItem('token');
    
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers
        });
        
        if (response.status === 401) {
            // Token expired
            localStorage.clear();
            window.location.href = 'login.html';
            throw new Error('Session expired');
        }
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'API request failed');
        }
        
        return data;
    } catch (error) {
        console.error('API request error:', error);
        throw error;
    }
}

// ========== NOTIFICATION SYSTEM ==========
function showNotification(message, type = 'info') {
    // Remove existing notification
    const existing = document.querySelector('.notification');
    if (existing) existing.remove();
    
    // Create notification
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        </div>
        <button class="notification-close">&times;</button>
    `;
    
    // Add styles if not already added
    if (!document.querySelector('#notification-styles')) {
        const styles = document.createElement('style');
        styles.id = 'notification-styles';
        styles.textContent = `
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                background: white;
                padding: 15px 20px;
                border-radius: 10px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.15);
                display: flex;
                align-items: center;
                justify-content: space-between;
                z-index: 9999;
                animation: slideIn 0.3s ease;
                max-width: 400px;
                border-left: 5px solid #667eea;
            }
            
            .notification-success { border-left-color: #10b981; }
            .notification-error { border-left-color: #ef4444; }
            .notification-warning { border-left-color: #f59e0b; }
            
            .notification-content {
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .notification-content i {
                font-size: 20px;
            }
            
            .notification-success i { color: #10b981; }
            .notification-error i { color: #ef4444; }
            .notification-warning i { color: #f59e0b; }
            
            .notification-close {
                background: none;
                border: none;
                font-size: 20px;
                cursor: pointer;
                color: #666;
                margin-left: 15px;
            }
            
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(styles);
    }
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
    
    // Close button
    notification.querySelector('.notification-close').addEventListener('click', () => {
        notification.remove();
    });
}

// ========== EXPORT ==========
window.apiRequest = apiRequest;
window.showNotification = showNotification;