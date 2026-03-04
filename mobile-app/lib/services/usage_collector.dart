import 'dart:async';
import 'package:flutter/material.dart';
import 'package:device_info_plus/device_info_plus.dart';
import 'package:usage_stats/usage_stats.dart';
import 'package:fatigue_mobile_app/services/api_service.dart';
import 'package:fatigue_mobile_app/providers/auth_provider.dart';
import 'package:provider/provider.dart';

class UsageCollector {

  static final UsageCollector _instance = UsageCollector._internal();
  factory UsageCollector() => _instance;
  UsageCollector._internal();

  final ApiService _apiService = ApiService();
  final DeviceInfoPlugin deviceInfo = DeviceInfoPlugin();

  Timer? _timer;

  String? _deviceId;
  String? _userId;

  Future<void> initialize() async {
    await _initDevice();
    await _requestPermission();
  }

  Future<void> _initDevice() async {
    try {
      final info = await deviceInfo.androidInfo;
      _deviceId = info.id.isNotEmpty
          ? info.id
          : "android_${DateTime.now().millisecondsSinceEpoch}";
    } catch (_) {
      _deviceId = "unknown_${DateTime.now().millisecondsSinceEpoch}";
    }
  }

  Future<void> _requestPermission() async {
    try {
      bool granted = await UsageStats.checkUsagePermission();
      if (!granted) {
        await UsageStats.grantUsagePermission();
      }
    } catch (e) {
      debugPrint("Permission error: $e");
    }
  }

  void startCollection(BuildContext context) {
    stopCollection();

    _timer = Timer.periodic(const Duration(minutes: 1), (_) {
      _collectAndSend(context);
    });

    WidgetsBinding.instance.addPostFrameCallback((_) {
      _collectAndSend(context);
    });
  }

  void stopCollection() {
    _timer?.cancel();
    _timer = null;
  }

  Future<void> _collectAndSend(BuildContext context) async {
    try {
      final auth = Provider.of<AuthProvider>(context, listen: false);
      _userId = auth.userId;

      if (_userId == null || _deviceId == null) return;

      final usage = await _collectUsage();

      await _apiService.sendMobileUsage(
        deviceId: _deviceId!,
        userId: _userId!,
        usageData: usage,
      );
    } catch (e) {
      debugPrint("Mobile usage error: $e");
    }
  }

  Future<Map<String, dynamic>> _collectUsage() async {

    final end = DateTime.now();
    final start = end.subtract(const Duration(minutes: 1));

    List<UsageInfo> stats = [];

    try {
      stats = await UsageStats.queryUsageStats(start, end);
    } catch (_) {
      stats = [];
    }

    double totalMillis = 0;
    String topApp = "Unknown";

    if (stats.isNotEmpty) {

      stats.sort((a, b) =>
          (b.totalTimeInForeground).compareTo(a.totalTimeInForeground));

      topApp = stats.first.packageName ?? "Unknown";

      totalMillis = stats.fold(
          0,
          (sum, item) =>
              sum + item.totalTimeInForeground);
    }

    final screenMinutes = totalMillis / 1000 / 60;

    return {
      "timestamp": DateTime.now().toIso8601String(),
      "session_id": "mobile_${DateTime.now().millisecondsSinceEpoch}",
      "app_name": topApp,
      "screen_time": screenMinutes,
      "category": _detectCategory(topApp),
      "notifications_received": 0
    };
  }

  String _detectCategory(String pkg) {

    pkg = pkg.toLowerCase();

    if (pkg.contains("youtube") || pkg.contains("netflix"))
      return "Entertainment";

    if (pkg.contains("whatsapp") ||
        pkg.contains("instagram") ||
        pkg.contains("facebook"))
      return "Social";

    if (pkg.contains("docs") ||
        pkg.contains("office") ||
        pkg.contains("code") ||
        pkg.contains("notion"))
      return "Productivity";

    return "Other";
  }

  Future<Map<String, dynamic>> getUsageSummary() async {

    final end = DateTime.now();
    final start = end.subtract(const Duration(hours: 24));

    List<UsageInfo> stats = [];

    try {
      stats = await UsageStats.queryUsageStats(start, end);
    } catch (_) {
      stats = [];
    }

    double totalMillis = stats.fold(
        0,
        (sum, item) =>
            sum + item.totalTimeInForeground);

    String topApp = "Unknown";

    if (stats.isNotEmpty) {

      stats.sort((a, b) =>
          (b.totalTimeInForeground).compareTo(a.totalTimeInForeground));

      topApp = stats.first.packageName ?? "Unknown";
    }

    return {
      "today_screen_time": totalMillis / 1000 / 60,
      "most_used_app": topApp,
      "productivity_score": _calculateProductivity(stats),
      "notification_count": 0
    };
  }

  int _calculateProductivity(List<UsageInfo> stats) {

    double productive = 0;
    double total = 0;

    for (final app in stats) {

      final t = app.totalTimeInForeground;

      total += t;

      final pkg = (app.packageName ?? "").toLowerCase();

      if (pkg.contains("docs") ||
          pkg.contains("code") ||
          pkg.contains("office")) {
        productive += t;
      }
    }

    if (total == 0) return 70;

    return ((productive / total) * 100).round();
  }
}