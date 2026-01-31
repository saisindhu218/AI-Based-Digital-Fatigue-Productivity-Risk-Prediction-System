import 'package:flutter/material.dart';
import 'package:fatigue_mobile_app/services/api_service.dart';
import 'package:fatigue_mobile_app/services/usage_collector.dart';
import 'package:provider/provider.dart';

class UsageProvider with ChangeNotifier {
  double _fatigueScore = 0.0;
  String _fatigueLevel = 'Low';
  double _productivityLoss = 0.0;
  double _todayScreenTime = 0.0;
  int _focusSessions = 0;
  int _notificationCount = 0;
  bool _laptopConnected = false;
  bool _mobileConnected = true;
  List<String> _recommendations = [];
  List<double> _usageData = [];
  bool _isLoading = false;
  String? _error;
  
  // Getters
  double get fatigueScore => _fatigueScore;
  String get fatigueLevel => _fatigueLevel;
  double get productivityLoss => _productivityLoss;
  double get todayScreenTime => _todayScreenTime;
  int get focusSessions => _focusSessions;
  int get notificationCount => _notificationCount;
  bool get laptopConnected => _laptopConnected;
  bool get mobileConnected => _mobileConnected;
  List<String> get recommendations => _recommendations;
  List<double> get usageData => _usageData;
  bool get isLoading => _isLoading;
  String? get error => _error;
  
  // Services
  final ApiService _apiService = ApiService();
  final UsageCollector _usageCollector = UsageCollector();
  
  Future<void> loadDashboardData() async {
    try {
      _setLoading(true);
      _error = null;
      
      // Start usage collection
      await _usageCollector.initialize();
      
      // Get usage summary
      final usageSummary = await _usageCollector.getUsageSummary();
      _todayScreenTime = usageSummary['today_screen_time'] ?? 0.0;
      _focusSessions = usageSummary['focus_sessions'] ?? 0;
      _notificationCount = usageSummary['notification_count'] ?? 0;
      
      // Load predictions from API
      await _loadPredictions();
      
      // Generate mock usage data for chart
      _generateUsageChartData();
      
      // Generate mock recommendations
      _generateRecommendations();
      
      notifyListeners();
      
    } catch (e) {
      _error = e.toString();
      // Load mock data for demo purposes
      _loadMockData();
    } finally {
      _setLoading(false);
    }
  }
  
  Future<void> _loadPredictions() async {
    try {
      // In production, this would call the API
      // For demo, use mock data
      _fatigueScore = 65.0;
      _fatigueLevel = _getFatigueLevel(_fatigueScore);
      _productivityLoss = 12.5;
      
    } catch (e) {
      // Fallback to mock data
      _fatigueScore = 65.0;
      _fatigueLevel = 'Medium';
      _productivityLoss = 12.5;
    }
  }
  
  String _getFatigueLevel(double score) {
    if (score >= 70) return 'High';
    if (score >= 40) return 'Medium';
    return 'Low';
  }
  
  void _generateUsageChartData() {
    // Generate mock usage data for the past 7 days
    final random = Random();
    _usageData = List.generate(7, (index) => random.nextDouble() * 100);
  }
  
  void _generateRecommendations() {
    _recommendations = [
      'Take a 15-minute break every 90 minutes',
      'Practice the 20-20-20 rule for eye strain',
      'Stay hydrated - aim for 8 glasses of water daily',
      'Take a short walk after 2 hours of continuous work',
      'Consider using blue light filter in the evening'
    ];
  }
  
  void _loadMockData() {
    // Mock data for demo purposes
    _fatigueScore = 65.0;
    _fatigueLevel = 'Medium';
    _productivityLoss = 12.5;
    _todayScreenTime = 320.0; // 5.3 hours in minutes
    _focusSessions = 8;
    _notificationCount = 42;
    _laptopConnected = true;
    _mobileConnected = true;
    
    _generateRecommendations();
    _generateUsageChartData();
  }
  
  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }
  
  void clearError() {
    _error = null;
    notifyListeners();
  }
  
  Future<void> refreshData() async {
    await loadDashboardData();
  }
  
  void updateDeviceStatus(bool laptopConnected, bool mobileConnected) {
    _laptopConnected = laptopConnected;
    _mobileConnected = mobileConnected;
    notifyListeners();
  }
  
  void addRecommendation(String recommendation) {
    _recommendations.insert(0, recommendation);
    notifyListeners();
  }
}