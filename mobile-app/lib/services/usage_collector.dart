import 'package:flutter/material.dart';
import 'package:device_info_plus/device_info_plus.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:fatigue_mobile_app/services/api_service.dart';
import 'package:fatigue_mobile_app/providers/auth_provider.dart';
import 'package:provider/provider.dart';

class UsageCollector {
  static final UsageCollector _instance = UsageCollector._internal();
  factory UsageCollector() => _instance;
  UsageCollector._internal();

  final ApiService _apiService = ApiService();
  final DeviceInfoPlugin deviceInfo = DeviceInfoPlugin();
  Timer? _collectionTimer;
  String? _deviceId;
  String? _userId;

  Future<void> initialize() async {
    await _getDeviceInfo();
    await _requestPermissions();
  }

  Future<void> _getDeviceInfo() async {
    try {
      final info = await deviceInfo.deviceInfo;
      _deviceId = info.data['id'] ?? 'unknown_device';
    } catch (e) {
      _deviceId = 'error_device_${DateTime.now().millisecondsSinceEpoch}';
    }
  }

  Future<void> _requestPermissions() async {
    // Request usage access permission
    final status = await Permission.usage.request();
    if (!status.isGranted) {
      debugPrint('Usage permission not granted');
    }
  }

  void startCollection(BuildContext context) {
    // Stop existing timer if any
    stopCollection();

    // Start new collection timer (every 5 minutes)
    _collectionTimer = Timer.periodic(const Duration(minutes: 5), (timer) {
      _collectAndSendUsage(context);
    });

    // Initial collection
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _collectAndSendUsage(context);
    });
  }

  void stopCollection() {
    _collectionTimer?.cancel();
    _collectionTimer = null;
  }

  Future<void> _collectAndSendUsage(BuildContext context) async {
    try {
      final authProvider = Provider.of<AuthProvider>(context, listen: false);
      _userId = authProvider.userId;

      if (_userId == null || _deviceId == null) {
        return;
      }

      // Collect usage data
      final usageData = await _collectUsageData();

      // Send to backend
      await _apiService.sendMobileUsage(
        deviceId: _deviceId!,
        userId: _userId!,
        usageData: usageData,
      );

      debugPrint('Usage data sent successfully');
    } catch (e) {
      debugPrint('Error collecting/sending usage: $e');
    }
  }

  Future<Map<String, dynamic>> _collectUsageData() async {
    // In a real app, you would use platform-specific APIs to collect usage data
    // For demo purposes, we'll simulate usage data
    
    final now = DateTime.now();
    final packageInfo = await PackageInfo.fromPlatform();

    return {
      'timestamp': now.toIso8601String(),
      'session_id': 'mobile_session_${now.millisecondsSinceEpoch}',
      'app_name': packageInfo.appName,
      'screen_time': _simulateScreenTime(),
      'category': _getAppCategory(packageInfo.appName),
      'notifications_received': _simulateNotifications(),
      'device_info': {
        'platform': Theme.of(context).platform.toString(),
        'app_version': packageInfo.version,
      },
    };
  }

  double _simulateScreenTime() {
    // Simulate screen time: 1-15 minutes in last 5 minutes
    return (Random().nextInt(15) + 1).toDouble();
  }

  int _simulateNotifications() {
    // Simulate notifications: 0-5 in last 5 minutes
    return Random().nextInt(6);
  }

  String _getAppCategory(String appName) {
    const socialApps = ['Facebook', 'Instagram', 'Twitter', 'WhatsApp'];
    const productivityApps = ['Gmail', 'Calendar', 'Docs', 'Slack'];
    const entertainmentApps = ['YouTube', 'Netflix', 'Spotify', 'Games'];

    if (socialApps.any((app) => appName.contains(app))) {
      return 'Social';
    } else if (productivityApps.any((app) => appName.contains(app))) {
      return 'Productivity';
    } else if (entertainmentApps.any((app) => appName.contains(app))) {
      return 'Entertainment';
    } else {
      return 'Other';
    }
  }

  Future<Map<String, dynamic>> getUsageSummary() async {
    // Get summarized usage data for display
    return {
      'today_screen_time': Random().nextInt(300) + 60, // 1-5 hours in minutes
      'most_used_app': 'WhatsApp',
      'productivity_score': Random().nextInt(40) + 60, // 60-100
      'notification_count': Random().nextInt(50) + 10,
    };
  }
}