// App Constants
class AppConstants {
  // API Configuration
  static const String apiBaseUrl = 'http://localhost:8000';
  static const String apiVersion = 'v1';
  
  // App Colors
  static const Color primaryColor = Color(0xFF4A90E2);
  static const Color secondaryColor = Color(0xFF7B68EE);
  static const Color successColor = Color(0xFF50C878);
  static const Color warningColor = Color(0xFFFFA500);
  static const Color dangerColor = Color(0xFFFF6B6B);
  static const Color darkColor = Color(0xFF2C3E50);
  static const Color lightColor = Color(0xFFF5F7FA);
  
  // App Strings
  static const String appName = 'FatigueGuard';
  static const String appDescription = 'AI-Powered Digital Fatigue Detection';
  static const String appVersion = '1.0.0';
  
  // Storage Keys
  static const String storageUserId = 'user_id';
  static const String storageAuthToken = 'auth_token';
  static const String storageUserEmail = 'user_email';
  static const String storageUserName = 'user_name';
  static const String storageDeviceId = 'device_id';
  static const String storageIsFirstLaunch = 'is_first_launch';
  
  // Notification Channels
  static const String notificationChannelId = 'fatigue_alerts';
  static const String notificationChannelName = 'Fatigue Alerts';
  static const String notificationChannelDescription = 'Notifications for fatigue alerts and recommendations';
  
  // Time Constants
  static const Duration dataSyncInterval = Duration(minutes: 5);
  static const Duration notificationCheckInterval = Duration(minutes: 15);
  static const Duration qrCodeExpiry = Duration(minutes: 5);
  
  // Thresholds
  static const double fatigueHighThreshold = 70.0;
  static const double productivityLossThreshold = 10.0; // hours/week
  static const int maxScreenTimeDaily = 600; // 10 hours in minutes
  
  // URLs
  static const String privacyPolicyUrl = 'https://example.com/privacy';
  static const String termsOfServiceUrl = 'https://example.com/terms';
  static const String supportEmail = 'support@fatigueguard.com';
  
  // Default values
  static const String defaultUserName = 'User';
  static const String defaultUserEmail = 'user@example.com';
  
  // Mock data for development
  static List<Map<String, dynamic>> mockNotifications = [
    {
      'id': '1',
      'title': 'Welcome to FatigueGuard',
      'message': 'Start tracking your digital wellness journey',
      'type': 'system',
      'priority': 'low',
      'read': true,
    },
    {
      'id': '2',
      'title': 'Device Pairing Available',
      'message': 'Pair your laptop for complete insights',
      'type': 'system',
      'priority': 'medium',
      'read': false,
    },
  ];
  
  static List<Map<String, dynamic>> mockRecommendations = [
    'Take a 15-minute break every 90 minutes',
    'Practice the 20-20-20 rule for eye strain',
    'Stay hydrated throughout the day',
    'Take a short walk after 2 hours of continuous work',
    'Use blue light filter in the evening',
    'Ensure 7-8 hours of quality sleep',
  ];
}

// API Endpoints
class ApiEndpoints {
  static String get baseUrl => '${AppConstants.apiBaseUrl}/api/${AppConstants.apiVersion}';
  
  // Authentication
  static String get login => '$baseUrl/auth/login';
  static String get register => '$baseUrl/auth/register';
  
  // Device Pairing
  static String get generateQR => '$baseUrl/pairing/generate-qr';
  static String get verifyPairing => '$baseUrl/pairing/verify-pairing';
  
  // Usage Data
  static String get laptopUsage => '$baseUrl/usage/laptop';
  static String get mobileUsage => '$baseUrl/usage/mobile';
  static String get userUsage => '$baseUrl/usage/user';
  
  // Predictions
  static String get predict => '$baseUrl/prediction/predict';
  static String get predictionHistory => '$baseUrl/prediction/user';
  
  // Notifications
  static String get notifications => '$baseUrl/notifications';
  static String userNotifications(String userId) => '$baseUrl/notifications/user/$userId';
}

// Shared Preferences Helper
class StorageHelper {
  static Future<void> saveString(String key, String value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(key, value);
  }
  
  static Future<String?> getString(String key) async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(key);
  }
  
  static Future<void> saveBool(String key, bool value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(key, value);
  }
  
  static Future<bool?> getBool(String key) async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getBool(key);
  }
  
  static Future<void> clearAll() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
  }
}

// Validation Helpers
class Validators {
  static bool isValidEmail(String email) {
    final emailRegex = RegExp(
      r'^[a-zA-Z0-9.]+@[a-zA-Z0-9]+\.[a-zA-Z]+',
    );
    return emailRegex.hasMatch(email);
  }
  
  static bool isValidPassword(String password) {
    return password.length >= 6;
  }
  
  static bool isValidName(String name) {
    return name.trim().length >= 2;
  }
}

// Format Helpers
class FormatHelpers {
  static String formatDuration(int minutes) {
    if (minutes < 60) {
      return '$minutes min';
    } else {
      final hours = minutes ~/ 60;
      final remainingMinutes = minutes % 60;
      if (remainingMinutes == 0) {
        return '$hours hr';
      } else {
        return '$hours hr $remainingMinutes min';
      }
    }
  }
  
  static String formatDateTime(DateTime dateTime) {
    final now = DateTime.now();
    final difference = now.difference(dateTime);
    
    if (difference.inMinutes < 1) {
      return 'Just now';
    } else if (difference.inHours < 1) {
      return '${difference.inMinutes}m ago';
    } else if (difference.inDays < 1) {
      return '${difference.inHours}h ago';
    } else if (difference.inDays < 7) {
      return '${difference.inDays}d ago';
    } else {
      return '${dateTime.day}/${dateTime.month}/${dateTime.year}';
    }
  }
  
  static String formatPercentage(double value) {
    return '${value.round()}%';
  }
  
  static String formatProductivityLoss(double hours) {
    return '${hours.toStringAsFixed(1)} hrs/week';
  }
}