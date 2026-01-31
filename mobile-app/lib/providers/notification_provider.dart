import 'package:flutter/material.dart';
import 'package:fatigue_mobile_app/services/api_service.dart';

class NotificationProvider with ChangeNotifier {
  List<NotificationItem> _notifications = [];
  bool _isLoading = false;
  String? _error;
  
  // Getters
  List<NotificationItem> get notifications => _notifications;
  bool get isLoading => _isLoading;
  String? get error => _error;
  int get unreadCount => _notifications.where((n) => !n.read).length;
  
  // Service
  final ApiService _apiService = ApiService();
  
  static Future<void> initialize() async {
    // Static initialization if needed
  }
  
  Future<void> loadNotifications() async {
    try {
      _setLoading(true);
      _error = null;
      
      // Load from API
      final response = await _apiService.getNotifications();
      
      if (response['success']) {
        final List<dynamic> data = response['notifications'] ?? [];
        _notifications = data.map((item) {
          return NotificationItem(
            id: item['id'] ?? '',
            title: item['title'] ?? '',
            message: item['message'] ?? '',
            type: item['type'] ?? 'system',
            priority: item['priority'] ?? 'low',
            timestamp: DateTime.parse(item['timestamp'] ?? DateTime.now().toIso8601String()),
            read: item['read'] ?? false,
            data: item['data'],
          );
        }).toList();
      } else {
        // Load mock data for demo
        _loadMockNotifications();
      }
      
      notifyListeners();
      
    } catch (e) {
      _error = e.toString();
      // Load mock data on error
      _loadMockNotifications();
    } finally {
      _setLoading(false);
    }
  }
  
  void _loadMockNotifications() {
    _notifications = [
      NotificationItem(
        id: '1',
        title: 'High Fatigue Alert',
        message: 'Your fatigue level has reached 75%. Consider taking a break.',
        type: 'fatigue_alert',
        priority: 'high',
        timestamp: DateTime.now().subtract(const Duration(minutes: 30)),
      ),
      NotificationItem(
        id: '2',
        title: 'Productivity Recommendation',
        message: 'Try the Pomodoro technique for better focus.',
        type: 'recommendation',
        priority: 'medium',
        timestamp: DateTime.now().subtract(const Duration(hours: 2)),
        read: true,
      ),
      NotificationItem(
        id: '3',
        title: 'Device Paired',
        message: 'Your laptop has been successfully paired.',
        type: 'system',
        priority: 'low',
        timestamp: DateTime.now().subtract(const Duration(hours: 5)),
        read: true,
      ),
      NotificationItem(
        id: '4',
        title: 'Screen Time Alert',
        message: 'You\'ve exceeded 6 hours of screen time today.',
        type: 'productivity_alert',
        priority: 'medium',
        timestamp: DateTime.now().subtract(const Duration(hours: 8)),
      ),
      NotificationItem(
        id: '5',
        title: 'Daily Summary',
        message: 'You were most productive between 9-11 AM.',
        type: 'recommendation',
        priority: 'low',
        timestamp: DateTime.now().subtract(const Duration(days: 1)),
        read: true,
      ),
    ];
  }
  
  Future<void> markAsRead(String id) async {
    try {
      // Update locally
      final index = _notifications.indexWhere((n) => n.id == id);
      if (index != -1) {
        _notifications[index] = NotificationItem(
          id: _notifications[index].id,
          title: _notifications[index].title,
          message: _notifications[index].message,
          type: _notifications[index].type,
          priority: _notifications[index].priority,
          timestamp: _notifications[index].timestamp,
          read: true,
          data: _notifications[index].data,
        );
        
        // Update on server
        await _apiService.markNotificationAsRead(id);
        
        notifyListeners();
      }
    } catch (e) {
      print('Error marking notification as read: $e');
    }
  }
  
  Future<void> markAsUnread(String id) async {
    try {
      final index = _notifications.indexWhere((n) => n.id == id);
      if (index != -1) {
        _notifications[index] = NotificationItem(
          id: _notifications[index].id,
          title: _notifications[index].title,
          message: _notifications[index].message,
          type: _notifications[index].type,
          priority: _notifications[index].priority,
          timestamp: _notifications[index].timestamp,
          read: false,
          data: _notifications[index].data,
        );
        
        await _apiService.markNotificationAsUnread(id);
        
        notifyListeners();
      }
    } catch (e) {
      print('Error marking notification as unread: $e');
    }
  }
  
  Future<void> markAllAsRead() async {
    try {
      for (var i = 0; i < _notifications.length; i++) {
        if (!_notifications[i].read) {
          _notifications[i] = NotificationItem(
            id: _notifications[i].id,
            title: _notifications[i].title,
            message: _notifications[i].message,
            type: _notifications[i].type,
            priority: _notifications[i].priority,
            timestamp: _notifications[i].timestamp,
            read: true,
            data: _notifications[i].data,
          );
          
          await _apiService.markNotificationAsRead(_notifications[i].id);
        }
      }
      
      notifyListeners();
    } catch (e) {
      print('Error marking all as read: $e');
    }
  }
  
  Future<void> deleteNotification(String id) async {
    try {
      _notifications.removeWhere((n) => n.id == id);
      await _apiService.deleteNotification(id);
      notifyListeners();
    } catch (e) {
      print('Error deleting notification: $e');
    }
  }
  
  void addNotification(NotificationItem notification) {
    _notifications.insert(0, notification);
    notifyListeners();
  }
  
  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }
  
  void clearError() {
    _error = null;
    notifyListeners();
  }
}