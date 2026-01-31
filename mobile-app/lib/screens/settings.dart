import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:fatigue_mobile_app/providers/auth_provider.dart';
import 'package:url_launcher/url_launcher.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({Key? key}) : super(key: key);

  @override
  _SettingsScreenState createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  bool _notificationsEnabled = true;
  bool _dataCollectionEnabled = true;
  bool _darkMode = false;
  bool _autoSync = true;
  String _syncFrequency = '15 minutes';

  @override
  Widget build(BuildContext context) {
    final authProvider = Provider.of<AuthProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Profile Section
          _buildSectionHeader('Profile'),
          Card(
            child: ListTile(
              leading: const CircleAvatar(
                backgroundImage: NetworkImage(
                  'https://ui-avatars.com/api/?name=John+Doe&background=4A90E2&color=fff',
                ),
              ),
              title: Text(
                authProvider.userName ?? 'User',
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
              subtitle: Text(authProvider.userEmail ?? 'user@example.com'),
              trailing: const Icon(Icons.edit),
              onTap: () {
                _showEditProfileDialog(context, authProvider);
              },
            ),
          ),

          const SizedBox(height: 20),

          // Preferences Section
          _buildSectionHeader('Preferences'),
          Card(
            child: Column(
              children: [
                SwitchListTile(
                  title: const Text('Enable Notifications'),
                  subtitle: const Text('Receive fatigue alerts and recommendations'),
                  value: _notificationsEnabled,
                  onChanged: (value) {
                    setState(() {
                      _notificationsEnabled = value;
                    });
                  },
                ),
                SwitchListTile(
                  title: const Text('Data Collection'),
                  subtitle: const Text('Allow usage data collection for insights'),
                  value: _dataCollectionEnabled,
                  onChanged: (value) {
                    setState(() {
                      _dataCollectionEnabled = value;
                    });
                  },
                ),
                SwitchListTile(
                  title: const Text('Dark Mode'),
                  subtitle: const Text('Use dark theme'),
                  value: _darkMode,
                  onChanged: (value) {
                    setState(() {
                      _darkMode = value;
                    });
                  },
                ),
                SwitchListTile(
                  title: const Text('Auto Sync'),
                  subtitle: const Text('Automatically sync data with server'),
                  value: _autoSync,
                  onChanged: (value) {
                    setState(() {
                      _autoSync = value;
                    });
                  },
                ),
                ListTile(
                  title: const Text('Sync Frequency'),
                  subtitle: Text(_syncFrequency),
                  trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                  onTap: () {
                    _showSyncFrequencyDialog(context);
                  },
                ),
              ],
            ),
          ),

          const SizedBox(height: 20),

          // Device Management Section
          _buildSectionHeader('Device Management'),
          Card(
            child: Column(
              children: [
                ListTile(
                  leading: const Icon(Icons.laptop, color: Colors.blue),
                  title: const Text('Laptop Device'),
                  subtitle: const Text('Connected 2 hours ago'),
                  trailing: Chip(
                    label: const Text('Paired', style: TextStyle(color: Colors.white)),
                    backgroundColor: Colors.green,
                  ),
                  onTap: () {
                    _showDeviceInfoDialog('Laptop');
                  },
                ),
                ListTile(
                  leading: const Icon(Icons.smartphone, color: Colors.green),
                  title: const Text('Mobile Device'),
                  subtitle: const Text('This device'),
                  trailing: Chip(
                    label: const Text('Active', style: TextStyle(color: Colors.white)),
                    backgroundColor: Colors.blue,
                  ),
                  onTap: () {
                    _showDeviceInfoDialog('Mobile');
                  },
                ),
                ListTile(
                  leading: const Icon(Icons.qr_code_scanner, color: Colors.purple),
                  title: const Text('Pair New Device'),
                  subtitle: const Text('Scan QR code to add device'),
                  trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                  onTap: () {
                    Navigator.pushNamed(context, '/qr-scanner');
                  },
                ),
              ],
            ),
          ),

          const SizedBox(height: 20),

          // About Section
          _buildSectionHeader('About'),
          Card(
            child: Column(
              children: [
                ListTile(
                  leading: const Icon(Icons.info_outline, color: Colors.blue),
                  title: const Text('About FatigueGuard'),
                  subtitle: const Text('Version 1.0.0'),
                  onTap: () {
                    _showAboutDialog(context);
                  },
                ),
                ListTile(
                  leading: const Icon(Icons.privacy_tip_outlined, color: Colors.green),
                  title: const Text('Privacy Policy'),
                  trailing: const Icon(Icons.open_in_new, size: 16),
                  onTap: () {
                    _launchUrl('https://example.com/privacy');
                  },
                ),
                ListTile(
                  leading: const Icon(Icons.description_outlined, color: Colors.orange),
                  title: const Text('Terms of Service'),
                  trailing: const Icon(Icons.open_in_new, size: 16),
                  onTap: () {
                    _launchUrl('https://example.com/terms');
                  },
                ),
                ListTile(
                  leading: const Icon(Icons.help_outline, color: Colors.purple),
                  title: const Text('Help & Support'),
                  trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                  onTap: () {
                    _showHelpDialog(context);
                  },
                ),
              ],
            ),
          ),

          const SizedBox(height: 20),

          // Danger Zone
          _buildSectionHeader('Account'),
          Card(
            color: Colors.red.withOpacity(0.05),
            child: Column(
              children: [
                ListTile(
                  leading: const Icon(Icons.logout, color: Colors.red),
                  title: const Text('Sign Out', style: TextStyle(color: Colors.red)),
                  onTap: () {
                    _showLogoutConfirmation(context, authProvider);
                  },
                ),
                ListTile(
                  leading: const Icon(Icons.delete_outline, color: Colors.red),
                  title: const Text('Delete Account', style: TextStyle(color: Colors.red)),
                  onTap: () {
                    _showDeleteAccountConfirmation(context);
                  },
                ),
              ],
            ),
          ),

          const SizedBox(height: 40),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Text(
        title,
        style: TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.w600,
          color: Colors.grey[600],
          letterSpacing: 0.5,
        ),
      ),
    );
  }

  void _showEditProfileDialog(BuildContext context, AuthProvider authProvider) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Edit Profile'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextFormField(
              initialValue: authProvider.userName,
              decoration: const InputDecoration(
                labelText: 'Full Name',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),
            TextFormField(
              initialValue: authProvider.userEmail,
              decoration: const InputDecoration(
                labelText: 'Email',
                border: OutlineInputBorder(),
              ),
              keyboardType: TextInputType.emailAddress,
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              // Save profile changes
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Profile updated')),
              );
            },
            child: const Text('Save'),
          ),
        ],
      ),
    );
  }

  void _showSyncFrequencyDialog(BuildContext context) {
    final frequencies = ['5 minutes', '15 minutes', '30 minutes', '1 hour'];
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Sync Frequency'),
        content: SizedBox(
          width: double.maxFinite,
          child: ListView.builder(
            shrinkWrap: true,
            itemCount: frequencies.length,
            itemBuilder: (context, index) {
              return RadioListTile<String>(
                title: Text(frequencies[index]),
                value: frequencies[index],
                groupValue: _syncFrequency,
                onChanged: (value) {
                  setState(() {
                    _syncFrequency = value!;
                  });
                  Navigator.pop(context);
                },
              );
            },
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
        ],
      ),
    );
  }

  void _showDeviceInfoDialog(String deviceType) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('$deviceType Device Info'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildInfoRow('Device Type', deviceType),
            _buildInfoRow('Status', 'Connected'),
            _buildInfoRow('Last Active', '2 hours ago'),
            _buildInfoRow('Connection', 'WiFi'),
            if (deviceType == 'Laptop')
              _buildInfoRow('IP Address', '192.168.1.100'),
            _buildInfoRow('Battery', '85%'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text('$deviceType device disconnected')),
              );
            },
            child: const Text('Disconnect', style: TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text('$label:', style: const TextStyle(fontWeight: FontWeight.w500)),
          Text(value),
        ],
      ),
    );
  }

  void _showAboutDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('About FatigueGuard'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'FatigueGuard is an AI-powered digital fatigue detection system that helps you maintain optimal productivity and wellness.',
              style: TextStyle(height: 1.5),
            ),
            const SizedBox(height: 16),
            _buildAboutInfo('Version', '1.0.0'),
            _buildAboutInfo('Build', '2024.01.001'),
            _buildAboutInfo('Developer', 'FatigueGuard Team'),
            _buildAboutInfo('License', 'MIT License'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  Widget _buildAboutInfo(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          SizedBox(
            width: 80,
            child: Text('$label:', style: const TextStyle(fontWeight: FontWeight.w500)),
          ),
          Text(value),
        ],
      ),
    );
  }

  void _showHelpDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Help & Support'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Need help? Here are some resources:',
              style: TextStyle(height: 1.5),
            ),
            const SizedBox(height: 16),
            ListTile(
              leading: const Icon(Icons.email, size: 20),
              title: const Text('Email Support'),
              subtitle: const Text('support@fatigueguard.com'),
              onTap: () => _launchUrl('mailto:support@fatigueguard.com'),
            ),
            ListTile(
              leading: const Icon(Icons.chat, size: 20),
              title: const Text('Live Chat'),
              subtitle: const Text('Available 9AM-6PM'),
              onTap: () {
                // Implement live chat
              },
            ),
            ListTile(
              leading: const Icon(Icons.book, size: 20),
              title: const Text('User Guide'),
              subtitle: const Text('Complete documentation'),
              onTap: () => _launchUrl('https://docs.fatigueguard.com'),
            ),
            ListTile(
              leading: const Icon(Icons.bug_report, size: 20),
              title: const Text('Report a Bug'),
              subtitle: const Text('Found an issue? Let us know'),
              onTap: () => _launchUrl('https://github.com/fatigueguard/issues'),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  void _showLogoutConfirmation(BuildContext context, AuthProvider authProvider) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Sign Out'),
        content: const Text('Are you sure you want to sign out?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              authProvider.logout();
              Navigator.pop(context);
              Navigator.pushReplacementNamed(context, '/login');
            },
            child: const Text('Sign Out', style: TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );
  }

  void _showDeleteAccountConfirmation(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Account'),
        content: const Text(
          'This action cannot be undone. All your data will be permanently deleted.',
          style: TextStyle(height: 1.5),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              _showFinalDeleteConfirmation(context);
            },
            child: const Text('Continue', style: TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );
  }

  void _showFinalDeleteConfirmation(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Final Confirmation'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('Type "DELETE" to confirm account deletion:'),
            const SizedBox(height: 16),
            TextFormField(
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                hintText: 'Type DELETE here',
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Account deletion scheduled'),
                  backgroundColor: Colors.red,
                ),
              );
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Delete Account'),
          ),
        ],
      ),
    );
  }

  Future<void> _launchUrl(String url) async {
    if (await canLaunch(url)) {
      await launch(url);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Could not launch $url')),
      );
    }
  }
}