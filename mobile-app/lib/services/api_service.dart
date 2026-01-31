import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  static const String _baseUrl = 'http://localhost:8000/api/v1';
  
  Future<Map<String, dynamic>> login(String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/auth/login'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'email': email,
          'password': password,
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return {
          'success': true,
          'user_id': data['user_id'] ?? email,
          'access_token': data['access_token'],
          'user_name': email.split('@')[0],
        };
      } else {
        return {
          'success': false,
          'error': 'Invalid email or password',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': 'Network error: $e',
      };
    }
  }
  
  Future<Map<String, dynamic>> register(String name, String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/auth/register'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'email': email,
          'full_name': name,
          'password': password,
        }),
      );

      if (response.statusCode == 200) {
        return {
          'success': true,
        };
      } else {
        final error = json.decode(response.body);
        return {
          'success': false,
          'error': error['detail'] ?? 'Registration failed',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': 'Network error: $e',
      };
    }
  }
  
  Future<Map<String, dynamic>> verifyPairing({
    required String token,
    required String deviceId,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/pairing/verify-pairing'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'token': token,
          'scanning_device_id': deviceId,
        }),
      );

      if (response.statusCode == 200) {
        return {
          'success': true,
        };
      } else {
        return {
          'success': false,
          'error': 'Pairing failed',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': 'Network error: $e',
      };
    }
  }
  
  Future<void> sendMobileUsage({
    required String deviceId,
    required String userId,
    required Map<String, dynamic> usageData,
  }) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('auth_token');
      
      await http.post(
        Uri.parse('$_baseUrl/usage/mobile'),
        headers: {
          'Content-Type': 'application/json',
          if (token != null) 'Authorization': 'Bearer $token',
        },
        body: json.encode({
          'device_id': deviceId,
          'user_id': userId,
          ...usageData,
        }),
      );
    } catch (e) {
      print('Error sending usage data: $e');
    }
  }
  
  Future<Map<String, dynamic>> getPredictions(String userId) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('auth_token');
      
      final response = await http.post(
        Uri.parse('$_baseUrl/prediction/predict'),
        headers: {
          'Content-Type': 'application/json',
          if (token != null) 'Authorization': 'Bearer $token',
        },
        body: json.encode({
          'user_id': userId,
          'timestamp': DateTime.now().toIso8601String(),
          'features': {},
        }),
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to load predictions');
      }
    } catch (e) {
      // Return mock data for demo
      return {
        'fatigue_score': 65.0,
        'fatigue_level': 'Medium',
        'productivity_loss': 12.5,
        'confidence': 0.85,
        'peak_hours': ['09:00-12:00'],
        'fatigue_prone_windows': ['14:00-16:00'],
        'recommendations': [
          'Take regular breaks every 45-50 minutes',
          'Practice the 20-20-20 rule for eye strain',
          'Stay hydrated throughout the day',
        ],
      };
    }
  }
  
  Future<Map<String, dynamic>> getNotifications() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('auth_token');
      final userId = prefs.getString('user_id');
      
      if (token == null || userId == null) {
        return {'success': false, 'notifications': []};
      }
      
      final response = await http.get(
        Uri.parse('$_baseUrl/notifications/user/$userId'),
        headers: {
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return {
          'success': true,
          'notifications': data,
        };
      } else {
        return {'success': false, 'notifications': []};
      }
    } catch (e) {
      return {'success': false, 'notifications': []};
    }
  }
  
  Future<void> markNotificationAsRead(String id) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('auth_token');
      
      await http.post(
        Uri.parse('$_baseUrl/notifications/$id/read'),
        headers: {
          if (token != null) 'Authorization': 'Bearer $token',
        },
      );
    } catch (e) {
      print('Error marking notification as read: $e');
    }
  }
  
  Future<void> markNotificationAsUnread(String id) async {
    // Note: This endpoint might not exist in the backend
    // For now, we'll just log it
    print('Marking notification $id as unread');
  }
  
  Future<void> deleteNotification(String id) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('auth_token');
      
      await http.delete(
        Uri.parse('$_baseUrl/notifications/$id'),
        headers: {
          if (token != null) 'Authorization': 'Bearer $token',
        },
      );
    } catch (e) {
      print('Error deleting notification: $e');
    }
  }
  
  // Get headers with authentication
  Future<Map<String, String>> getAuthHeaders() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('auth_token');
    
    return {
      'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };
  }
}