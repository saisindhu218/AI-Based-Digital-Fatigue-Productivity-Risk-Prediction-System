// Authentication module
class AuthManager {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000/api/v1';
        this.token = localStorage.getItem('authToken');
        this.user = JSON.parse(localStorage.getItem('user') || '{}');
    }

    async login(email, password) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, password })
            });

            if (!response.ok) {
                throw new Error('Login failed');
            }

            const data = await response.json();
            
            // Store tokens and user data
            localStorage.setItem('authToken', data.access_token);
            localStorage.setItem('tokenType', data.token_type);
            
            // Decode JWT to get user info (simplified)
            const tokenData = JSON.parse(atob(data.access_token.split('.')[1]));
            this.user = {
                email: tokenData.sub,
                userId: tokenData.sub // In production, get from user endpoint
            };
            
            localStorage.setItem('user', JSON.stringify(this.user));
            
            return { success: true, user: this.user };
            
        } catch (error) {
            console.error('Login error:', error);
            return { success: false, error: error.message };
        }
    }

    async register(fullName, email, password) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email: email,
                    full_name: fullName,
                    password: password
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Registration failed');
            }

            const userData = await response.json();
            
            // Auto-login after registration
            return await this.login(email, password);
            
        } catch (error) {
            console.error('Registration error:', error);
            return { success: false, error: error.message };
        }
    }

    logout() {
        localStorage.removeItem('authToken');
        localStorage.removeItem('tokenType');
        localStorage.removeItem('user');
        localStorage.removeItem('userId');
        this.token = null;
        this.user = {};
        
        // Redirect to login page
        window.location.href = 'login.html';
    }

    isAuthenticated() {
        const token = localStorage.getItem('authToken');
        if (!token) return false;

        // Check token expiration (simplified)
        try {
            const tokenData = JSON.parse(atob(token.split('.')[1]));
            const expiration = tokenData.exp * 1000; // Convert to milliseconds
            return Date.now() < expiration;
        } catch (error) {
            return false;
        }
    }

    getAuthHeaders() {
        const token = localStorage.getItem('authToken');
        return {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };
    }

    getCurrentUser() {
        return this.user;
    }

    async refreshToken() {
        // Implement token refresh logic
        // This would call a refresh endpoint if available
        console.log('Token refresh would be implemented here');
        return this.token;
    }
}

// Create global auth instance
window.authManager = new AuthManager();

// Login page functionality
if (window.location.pathname.includes('login.html') || 
    window.location.pathname === '/login') {
    
    document.addEventListener('DOMContentLoaded', function() {
        const loginForm = document.getElementById('login-form');
        
        if (loginForm) {
            loginForm.addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const email = document.getElementById('email').value;
                const password = document.getElementById('password').value;
                const submitBtn = document.querySelector('button[type="submit"]');
                const errorDiv = document.getElementById('error-message');
                
                // Show loading state
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Logging in...';
                
                if (errorDiv) errorDiv.style.display = 'none';
                
                try {
                    const result = await authManager.login(email, password);
                    
                    if (result.success) {
                        // Redirect to dashboard
                        window.location.href = 'index.html';
                    } else {
                        throw new Error(result.error);
                    }
                } catch (error) {
                    if (errorDiv) {
                        errorDiv.textContent = error.message;
                        errorDiv.style.display = 'block';
                    }
                    
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Login';
                }
            });
        }
        
        // Check if already logged in
        if (authManager.isAuthenticated()) {
            window.location.href = 'index.html';
        }
    });
}

// Register page functionality
if (window.location.pathname.includes('register.html') || 
    window.location.pathname === '/register') {
    
    document.addEventListener('DOMContentLoaded', function() {
        const registerForm = document.getElementById('register-form');
        
        if (registerForm) {
            registerForm.addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const fullName = document.getElementById('full-name').value;
                const email = document.getElementById('email').value;
                const password = document.getElementById('password').value;
                const confirmPassword = document.getElementById('confirm-password').value;
                const submitBtn = document.querySelector('button[type="submit"]');
                const errorDiv = document.getElementById('error-message');
                
                // Validate passwords match
                if (password !== confirmPassword) {
                    if (errorDiv) {
                        errorDiv.textContent = 'Passwords do not match';
                        errorDiv.style.display = 'block';
                    }
                    return;
                }
                
                // Validate password strength
                if (password.length < 6) {
                    if (errorDiv) {
                        errorDiv.textContent = 'Password must be at least 6 characters';
                        errorDiv.style.display = 'block';
                    }
                    return;
                }
                
                // Show loading state
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating account...';
                
                if (errorDiv) errorDiv.style.display = 'none';
                
                try {
                    const result = await authManager.register(fullName, email, password);
                    
                    if (result.success) {
                        // Redirect to dashboard
                        window.location.href = 'index.html';
                    } else {
                        throw new Error(result.error);
                    }
                } catch (error) {
                    if (errorDiv) {
                        errorDiv.textContent = error.message;
                        errorDiv.style.display = 'block';
                    }
                    
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Register';
                }
            });
        }
        
        // Check if already logged in
        if (authManager.isAuthenticated()) {
            window.location.href = 'index.html';
        }
    });
}

// Auto-check authentication on protected pages
if (!window.location.pathname.includes('login.html') && 
    !window.location.pathname.includes('register.html') &&
    window.location.pathname !== '/login' &&
    window.location.pathname !== '/register') {
    
    document.addEventListener('DOMContentLoaded', function() {
        if (!authManager.isAuthenticated()) {
            window.location.href = 'login.html';
        }
    });
}

// Logout functionality
document.addEventListener('DOMContentLoaded', function() {
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            authManager.logout();
        });
    }
});