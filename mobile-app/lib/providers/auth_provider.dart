import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:device_info_plus/device_info_plus.dart';
import 'package:fatigue_mobile_app/services/api_service.dart';

class AuthProvider with ChangeNotifier {
  String? _userId;
  String? _userName;
  String? _userEmail;
  String? _deviceId;
  String? _authToken;
  bool _isLoading = false;
  String? _error;
  
  // Getters
  String? get userId => _userId;
  String? get userName => _userName;
  String? get userEmail => _userEmail;
  String? get deviceId => _deviceId;
  String? get authToken => _authToken;
  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get isLoggedIn => _userId != null && _authToken != null;
  
  // Service
  final ApiService _apiService = ApiService();
  final DeviceInfoPlugin _deviceInfo = DeviceInfoPlugin();
  
  static Future<void> initialize() async {
    // Static initialization if needed
  }
  
  Future<void> login(String email, String password) async {
    try {
      _setLoading(true);
      _error = null;
      
      final response = await _apiService.login(email, password);
      
      if (response['success']) {
        _userId = response['user_id'];
        _userEmail = email;
        _authToken = response['access_token'];
        _userName = response['user_name'] ?? email.split('@')[0];
        
        // Get device ID
        await _getDeviceId();
        
        // Save to shared preferences
        await _saveAuthData();
        
        notifyListeners();
      } else {
        throw Exception(response['error'] ?? 'Login failed');
      }
    } catch (e) {
      _error = e.toString();
      rethrow;
    } finally {
      _setLoading(false);
    }
  }
  
  Future<void> register(String name, String email, String password) async {
    try {
      _setLoading(true);
      _error = null;
      
      final response = await _apiService.register(name, email, password);
      
      if (response['success']) {
        // Auto-login after registration
        await login(email, password);
      } else {
        throw Exception(response['error'] ?? 'Registration failed');
      }
    } catch (e) {
      _error = e.toString();
      rethrow;
    } finally {
      _setLoading(false);
    }
  }
  
  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
    
    _userId = null;
    _userName = null;
    _userEmail = null;
    _authToken = null;
    _error = null;
    
    notifyListeners();
  }
  
  Future<bool> checkIfLoggedIn() async {
    final prefs = await SharedPreferences.getInstance();
    
    final savedUserId = prefs.getString('user_id');
    final savedToken = prefs.getString('auth_token');
    final savedEmail = prefs.getString('user_email');
    final savedName = prefs.getString('user_name');
    
    if (savedUserId != null && savedToken != null) {
      _userId = savedUserId;
      _authToken = savedToken;
      _userEmail = savedEmail;
      _userName = savedName;
      
      // Get device ID
      await _getDeviceId();
      
      // Verify token is still valid (optional)
      final isValid = await _validateToken();
      if (!isValid) {
        await logout();
        return false;
      }
      
      notifyListeners();
      return true;
    }
    
    return false;
  }
  
  Future<void> _getDeviceId() async {
    try {
      final deviceInfo = await _deviceInfo.deviceInfo;
      _deviceId = 'mobile_${deviceInfo.data['id']}';
    } catch (e) {
      _deviceId = 'mobile_unknown_${DateTime.now().millisecondsSinceEpoch}';
    }
  }
  
  Future<void> _saveAuthData() async {
    final prefs = await SharedPreferences.getInstance();
    
    if (_userId != null) {
      await prefs.setString('user_id', _userId!);
    }
    if (_authToken != null) {
      await prefs.setString('auth_token', _authToken!);
    }
    if (_userEmail != null) {
      await prefs.setString('user_email', _userEmail!);
    }
    if (_userName != null) {
      await prefs.setString('user_name', _userName!);
    }
  }
  
  Future<bool> _validateToken() async {
    // Implement token validation logic
    // For now, return true if token exists
    return _authToken != null && _authToken!.isNotEmpty;
  }
  
  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }
  
  Future<void> setPairedUser(String userId) async {
    _userId = userId;
    await _saveAuthData();
    notifyListeners();
  }
  
  // Clear any error
  void clearError() {
    _error = null;
    notifyListeners();
  }
}