import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:fatigue_mobile_app/providers/usage_provider.dart';
import 'package:fatigue_mobile_app/providers/auth_provider.dart';
import 'package:fatigue_mobile_app/widgets/stat_card.dart';
import 'package:fatigue_mobile_app/widgets/fatigue_meter.dart';

class Dashboard extends StatefulWidget {
  const Dashboard({Key? key}) : super(key: key);

  @override
  _DashboardState createState() => _DashboardState();
}

class _DashboardState extends State<Dashboard> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadDashboardData();
    });
  }

  Future<void> _loadDashboardData() async {
    final usageProvider = Provider.of<UsageProvider>(context, listen: false);
    await usageProvider.loadDashboardData();
  }

  @override
  Widget build(BuildContext context) {
    final authProvider = Provider.of<AuthProvider>(context);
    final usageProvider = Provider.of<UsageProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Dashboard'),
        actions: [
          IconButton(
            icon: const Icon(Icons.qr_code_scanner),
            onPressed: () => Navigator.pushNamed(context, '/qr-scanner'),
          ),
          IconButton(
            icon: const Icon(Icons.notifications),
            onPressed: () => Navigator.pushNamed(context, '/notifications'),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () => usageProvider.loadDashboardData(),
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Welcome Section
              _buildWelcomeSection(authProvider.userName),
              const SizedBox(height: 20),

              // Fatigue Meter
              FatigueMeter(
                fatigueScore: usageProvider.fatigueScore,
                fatigueLevel: usageProvider.fatigueLevel,
              ),
              const SizedBox(height: 20),

              // Stats Grid
              _buildStatsGrid(usageProvider),
              const SizedBox(height: 20),

              // Usage Chart
              _buildUsageChart(usageProvider),
              const SizedBox(height: 20),

              // Recommendations
              _buildRecommendations(usageProvider.recommendations),
              const SizedBox(height: 20),

              // Device Status
              _buildDeviceStatus(usageProvider),
            ],
          ),
        ),
      ),
      bottomNavigationBar: _buildBottomNavBar(context),
    );
  }

  Widget _buildWelcomeSection(String? userName) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Hello, ${userName ?? 'User'}!',
          style: const TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          'Here\'s your digital fatigue overview',
          style: TextStyle(
            fontSize: 14,
            color: Colors.grey[600],
          ),
        ),
      ],
    );
  }

  Widget _buildStatsGrid(UsageProvider provider) {
    return GridView.count(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisCount: 2,
      crossAxisSpacing: 12,
      mainAxisSpacing: 12,
      childAspectRatio: 1.2,
      children: [
        StatCard(
          title: 'Productivity Loss',
          value: '${provider.productivityLoss.toStringAsFixed(1)} hrs',
          subtitle: 'Per week',
          icon: Icons.trending_down,
          color: Colors.orange,
        ),
        StatCard(
          title: 'Screen Time',
          value: '${(provider.todayScreenTime / 60).toStringAsFixed(1)} hrs',
          subtitle: 'Today',
          icon: Icons.smartphone,
          color: Colors.blue,
        ),
        StatCard(
          title: 'Focus Sessions',
          value: provider.focusSessions.toString(),
          subtitle: 'Today',
          icon: Icons.timer,
          color: Colors.green,
        ),
        StatCard(
          title: 'Notifications',
          value: provider.notificationCount.toString(),
          subtitle: 'Today',
          icon: Icons.notifications,
          color: Colors.purple,
        ),
      ],
    );
  }

  Widget _buildUsageChart(UsageProvider provider) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Daily Usage Pattern',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 16),
            SizedBox(
              height: 200,
              child: LineChart(
                LineChartData(
                  gridData: FlGridData(show: false),
                  titlesData: FlTitlesData(show: false),
                  borderData: FlBorderData(show: false),
                  lineBarsData: [
                    LineChartBarData(
                      spots: provider.usageData
                          .asMap()
                          .entries
                          .map((e) => FlSpot(
                                e.key.toDouble(),
                                e.value.toDouble(),
                              ))
                          .toList(),
                      isCurved: true,
                      color: Colors.blue,
                      barWidth: 3,
                      belowBarData: BarAreaData(show: false),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRecommendations(List<String> recommendations) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.lightbulb_outline, color: Colors.amber),
                const SizedBox(width: 8),
                const Text(
                  'AI Recommendations',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            ...recommendations.take(3).map((rec) => Padding(
                  padding: const EdgeInsets.symmetric(vertical: 4),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Icon(Icons.check_circle,
                          size: 16, color: Colors.green),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          rec,
                          style: const TextStyle(fontSize: 14),
                        ),
                      ),
                    ],
                  ),
                )),
          ],
        ),
      ),
    );
  }

  Widget _buildDeviceStatus(UsageProvider provider) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Device Status',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                _buildStatusIndicator('Laptop', provider.laptopConnected),
                const SizedBox(width: 16),
                _buildStatusIndicator('Mobile', provider.mobileConnected),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusIndicator(String device, bool connected) {
    return Row(
      children: [
        Container(
          width: 12,
          height: 12,
          decoration: BoxDecoration(
            color: connected ? Colors.green : Colors.red,
            shape: BoxShape.circle,
          ),
        ),
        const SizedBox(width: 8),
        Text(
          '$device: ${connected ? 'Connected' : 'Disconnected'}',
          style: TextStyle(
            color: connected ? Colors.green : Colors.red,
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
    );
  }

  Widget _buildBottomNavBar(BuildContext context) {
    return BottomNavigationBar(
      currentIndex: 0,
      type: BottomNavigationBarType.fixed,
      items: const [
        BottomNavigationBarItem(
          icon: Icon(Icons.dashboard),
          label: 'Dashboard',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.insights),
          label: 'Insights',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.settings),
          label: 'Settings',
        ),
      ],
      onTap: (index) {
        switch (index) {
          case 1:
            Navigator.pushNamed(context, '/insights');
            break;
          case 2:
            Navigator.pushNamed(context, '/settings');
            break;
        }
      },
    );
  }
}