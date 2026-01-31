import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:fatigue_mobile_app/providers/usage_provider.dart';
import 'package:fatigue_mobile_app/widgets/stat_card.dart';

class InsightsScreen extends StatefulWidget {
  const InsightsScreen({Key? key}) : super(key: key);

  @override
  _InsightsScreenState createState() => _InsightsScreenState();
}

class _InsightsScreenState extends State<InsightsScreen> {
  int _selectedTimeRange = 0; // 0: Today, 1: Week, 2: Month
  final List<String> _timeRanges = ['Today', 'Week', 'Month'];

  @override
  Widget build(BuildContext context) {
    final usageProvider = Provider.of<UsageProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Insights & Analytics'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: usageProvider.isLoading ? null : usageProvider.refreshData,
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () => usageProvider.refreshData(),
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Time range selector
              _buildTimeRangeSelector(),
              const SizedBox(height: 20),

              // Productivity Stats
              Text(
                'Productivity Overview',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                  color: Colors.grey[700],
                ),
              ),
              const SizedBox(height: 16),
              _buildProductivityStats(),

              const SizedBox(height: 24),

              // Usage Trends
              _buildUsageTrendsChart(usageProvider),

              const SizedBox(height: 24),

              // App Usage
              _buildAppUsageSection(),

              const SizedBox(height: 24),

              // Productivity Hours
              _buildProductivityHours(),

              const SizedBox(height: 40),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildTimeRangeSelector() {
    return Row(
      children: _timeRanges.asMap().entries.map((entry) {
        final index = entry.key;
        final label = entry.value;
        return Expanded(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 4),
            child: ElevatedButton(
              onPressed: () {
                setState(() {
                  _selectedTimeRange = index;
                });
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: _selectedTimeRange == index
                    ? const Color(0xFF4A90E2)
                    : Colors.grey[200],
                foregroundColor: _selectedTimeRange == index
                    ? Colors.white
                    : Colors.grey[700],
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
                elevation: 0,
                padding: const EdgeInsets.symmetric(vertical: 12),
              ),
              child: Text(label),
            ),
          ),
        );
      }).toList(),
    );
  }

  Widget _buildProductivityStats() {
    return GridView.count(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisCount: 2,
      crossAxisSpacing: 12,
      mainAxisSpacing: 12,
      childAspectRatio: 1.2,
      children: [
        StatCard(
          title: 'Focus Time',
          value: '3.2',
          subtitle: 'hours today',
          icon: Icons.timer,
          color: Colors.green,
        ),
        StatCard(
          title: 'Distractions',
          value: '18',
          subtitle: 'interruptions',
          icon: Icons.notifications_active,
          color: Colors.orange,
        ),
        StatCard(
          title: 'Task Complete',
          value: '85%',
          subtitle: 'completion rate',
          icon: Icons.check_circle,
          color: Colors.blue,
        ),
        StatCard(
          title: 'Breaks Taken',
          value: '7',
          subtitle: 'recommended breaks',
          icon: Icons.coffee,
          color: Colors.purple,
        ),
      ],
    );
  }

  Widget _buildUsageTrendsChart(UsageProvider provider) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Usage Trends',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.w600,
                    color: Colors.grey[700],
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.info_outline, size: 20),
                  onPressed: () {
                    // Show info about trends
                  },
                ),
              ],
            ),
            const SizedBox(height: 16),
            SizedBox(
              height: 200,
              child: LineChart(
                LineChartData(
                  gridData: FlGridData(
                    show: true,
                    drawVerticalLine: false,
                    horizontalInterval: 20,
                    getDrawingHorizontalLine: (value) {
                      return FlLine(
                        color: Colors.grey[300]!,
                        strokeWidth: 1,
                      );
                    },
                  ),
                  titlesData: FlTitlesData(
                    show: true,
                    rightTitles: const AxisTitles(
                      sideTitles: SideTitles(showTitles: false),
                    ),
                    topTitles: const AxisTitles(
                      sideTitles: SideTitles(showTitles: false),
                    ),
                    bottomTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        reservedSize: 30,
                        interval: 1,
                        getTitlesWidget: (value, meta) {
                          const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
                          if (value.toInt() < days.length) {
                            return Text(days[value.toInt()]);
                          }
                          return const Text('');
                        },
                      ),
                    ),
                    leftTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        interval: 20,
                        reservedSize: 40,
                        getTitlesWidget: (value, meta) {
                          return Text('${value.toInt()}%');
                        },
                      ),
                    ),
                  ),
                  borderData: FlBorderData(
                    show: false,
                  ),
                  minX: 0,
                  maxX: 6,
                  minY: 0,
                  maxY: 100,
                  lineBarsData: [
                    LineChartBarData(
                      spots: provider.usageData
                          .asMap()
                          .entries
                          .map((e) => FlSpot(e.key.toDouble(), e.value))
                          .toList(),
                      isCurved: true,
                      color: const Color(0xFF4A90E2),
                      barWidth: 3,
                      belowBarData: BarAreaData(
                        show: true,
                        color: const Color(0xFF4A90E2).withOpacity(0.1),
                      ),
                      dotData: const FlDotData(show: false),
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

  Widget _buildAppUsageSection() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'App Usage Breakdown',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w600,
                color: Colors.grey[700],
              ),
            ),
            const SizedBox(height: 16),
            ..._buildAppUsageList(),
          ],
        ),
      ),
    );
  }

  List<Widget> _buildAppUsageList() {
    final apps = [
      {'name': 'VS Code', 'time': '2.5h', 'category': 'Development', 'color': Colors.blue},
      {'name': 'Chrome', 'time': '1.8h', 'category': 'Browser', 'color': Colors.orange},
      {'name': 'Slack', 'time': '1.2h', 'category': 'Communication', 'color': Colors.purple},
      {'name': 'WhatsApp', 'time': '45m', 'category': 'Social', 'color': Colors.green},
      {'name': 'Spotify', 'time': '30m', 'category': 'Entertainment', 'color': Colors.greenAccent},
    ];

    return apps.map((app) {
      return Padding(
        padding: const EdgeInsets.symmetric(vertical: 8),
        child: Row(
          children: [
            Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: (app['color'] as Color).withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(
                Icons.apps,
                color: app['color'] as Color,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    app['name'] as String,
                    style: const TextStyle(
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  Text(
                    app['category'] as String,
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey[500],
                    ),
                  ),
                ],
              ),
            ),
            Text(
              app['time'] as String,
              style: const TextStyle(
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
      );
    }).toList();
  }

  Widget _buildProductivityHours() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.schedule, color: Colors.blue),
                const SizedBox(width: 8),
                Text(
                  'Peak Productivity Hours',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.w600,
                    color: Colors.grey[700],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            ..._buildProductivityHoursList(),
          ],
        ),
      ),
    );
  }

  List<Widget> _buildProductivityHoursList() {
    final hours = [
      {'time': '09:00 - 11:00', 'productivity': 'High', 'color': Colors.green},
      {'time': '11:00 - 13:00', 'productivity': 'Medium', 'color': Colors.orange},
      {'time': '13:00 - 15:00', 'productivity': 'Low', 'color': Colors.red},
      {'time': '15:00 - 17:00', 'productivity': 'High', 'color': Colors.green},
      {'time': '17:00 - 19:00', 'productivity': 'Medium', 'color': Colors.orange},
    ];

    return hours.map((hour) {
      return Padding(
        padding: const EdgeInsets.symmetric(vertical: 8),
        child: Row(
          children: [
            Expanded(
              child: Text(
                hour['time'] as String,
                style: const TextStyle(fontSize: 14),
              ),
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
              decoration: BoxDecoration(
                color: (hour['color'] as Color).withOpacity(0.1),
                borderRadius: BorderRadius.circular(20),
              ),
              child: Text(
                hour['productivity'] as String,
                style: TextStyle(
                  color: hour['color'] as Color,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
          ],
        ),
      );
    }).toList();
  }
}