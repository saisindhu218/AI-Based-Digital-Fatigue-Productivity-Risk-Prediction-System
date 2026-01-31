import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:fatigue_mobile_app/providers/notification_provider.dart';
import 'package:intl/intl.dart';

class NotificationsScreen extends StatefulWidget {
  const NotificationsScreen({Key? key}) : super(key: key);

  @override
  _NotificationsScreenState createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends State<NotificationsScreen> {
  String _selectedFilter = 'all'; // all, unread, alerts

  @override
  Widget build(BuildContext context) {
    final notificationProvider = Provider.of<NotificationProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Notifications'),
        actions: [
          // Filter dropdown
          PopupMenuButton<String>(
            onSelected: (value) {
              setState(() {
                _selectedFilter = value;
              });
            },
            itemBuilder: (context) => [
              const PopupMenuItem(
                value: 'all',
                child: Text('All Notifications'),
              ),
              const PopupMenuItem(
                value: 'unread',
                child: Text('Unread Only'),
              ),
              const PopupMenuItem(
                value: 'alerts',
                child: Text('Alerts Only'),
              ),
            ],
          ),
          IconButton(
            icon: const Icon(Icons.check_all),
            onPressed: () {
              notificationProvider.markAllAsRead();
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('All notifications marked as read'),
                ),
              );
            },
          ),
        ],
      ),
      body: notificationProvider.isLoading
          ? const Center(child: CircularProgressIndicator())
          : _buildNotificationList(notificationProvider),
    );
  }

  Widget _buildNotificationList(NotificationProvider provider) {
    final notifications = provider.notifications
        .where((n) {
          if (_selectedFilter == 'unread') return !n.read;
          if (_selectedFilter == 'alerts') return n.priority == 'high';
          return true;
        })
        .toList();

    if (notifications.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.notifications_none,
              size: 80,
              color: Colors.grey,
            ),
            const SizedBox(height: 16),
            Text(
              _selectedFilter == 'unread'
                  ? 'No unread notifications'
                  : _selectedFilter == 'alerts'
                      ? 'No alerts'
                      : 'No notifications yet',
              style: const TextStyle(
                fontSize: 18,
                color: Colors.grey,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'You\'re all caught up!',
              style: TextStyle(color: Colors.grey),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: () => provider.loadNotifications(),
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: notifications.length,
        itemBuilder: (context, index) {
          final notification = notifications[index];
          return _buildNotificationItem(notification, provider);
        },
      ),
    );
  }

  Widget _buildNotificationItem(
      NotificationItem notification, NotificationProvider provider) {
    return Dismissible(
      key: Key(notification.id),
      background: Container(
        color: Colors.red,
        alignment: Alignment.centerLeft,
        padding: const EdgeInsets.only(left: 20),
        child: const Icon(Icons.delete, color: Colors.white),
      ),
      secondaryBackground: Container(
        color: notification.read ? Colors.grey : Colors.blue,
        alignment: Alignment.centerRight,
        padding: const EdgeInsets.only(right: 20),
        child: Icon(
          notification.read ? Icons.mark_email_unread : Icons.mark_email_read,
          color: Colors.white,
        ),
      ),
      confirmDismiss: (direction) async {
        if (direction == DismissDirection.endToStart) {
          // Mark as read/unread
          if (notification.read) {
            await provider.markAsUnread(notification.id);
          } else {
            await provider.markAsRead(notification.id);
          }
          return false; // Don't dismiss
        } else {
          // Delete
          return await showDialog(
            context: context,
            builder: (context) => AlertDialog(
              title: const Text('Delete Notification'),
              content: const Text('Are you sure you want to delete this notification?'),
              actions: [
                TextButton(
                  onPressed: () => Navigator.of(context).pop(false),
                  child: const Text('Cancel'),
                ),
                TextButton(
                  onPressed: () {
                    provider.deleteNotification(notification.id);
                    Navigator.of(context).pop(true);
                  },
                  child: const Text('Delete', style: TextStyle(color: Colors.red)),
                ),
              ],
            ),
          );
        }
      },
      child: Card(
        elevation: notification.read ? 0 : 2,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        color: notification.read ? Colors.grey[50] : Colors.white,
        child: InkWell(
          onTap: () {
            if (!notification.read) {
              provider.markAsRead(notification.id);
            }
            // Handle notification tap
            _handleNotificationTap(notification);
          },
          borderRadius: BorderRadius.circular(12),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Notification icon
                Container(
                  width: 40,
                  height: 40,
                  decoration: BoxDecoration(
                    color: _getNotificationColor(notification.type).withOpacity(0.1),
                    shape: BoxShape.circle,
                  ),
                  child: Icon(
                    _getNotificationIcon(notification.type),
                    color: _getNotificationColor(notification.type),
                    size: 20,
                  ),
                ),
                const SizedBox(width: 12),
                
                // Notification content
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Expanded(
                            child: Text(
                              notification.title,
                              style: TextStyle(
                                fontWeight: notification.read
                                    ? FontWeight.normal
                                    : FontWeight.bold,
                                fontSize: 16,
                              ),
                            ),
                          ),
                          if (!notification.read)
                            Container(
                              width: 8,
                              height: 8,
                              decoration: const BoxDecoration(
                                color: Colors.blue,
                                shape: BoxShape.circle,
                              ),
                            ),
                        ],
                      ),
                      const SizedBox(height: 4),
                      Text(
                        notification.message,
                        style: TextStyle(
                          color: Colors.grey[600],
                          fontSize: 14,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 8,
                              vertical: 2,
                            ),
                            decoration: BoxDecoration(
                              color: _getPriorityColor(notification.priority)
                                  .withOpacity(0.1),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Text(
                              notification.priority.toUpperCase(),
                              style: TextStyle(
                                fontSize: 10,
                                color: _getPriorityColor(notification.priority),
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                          Text(
                            _formatTime(notification.timestamp),
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.grey[500],
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Color _getNotificationColor(String type) {
    switch (type) {
      case 'fatigue_alert':
        return Colors.red;
      case 'productivity_alert':
        return Colors.orange;
      case 'recommendation':
        return Colors.green;
      case 'system':
        return Colors.blue;
      default:
        return Colors.grey;
    }
  }

  IconData _getNotificationIcon(String type) {
    switch (type) {
      case 'fatigue_alert':
        return Icons.warning;
      case 'productivity_alert':
        return Icons.trending_down;
      case 'recommendation':
        return Icons.lightbulb;
      case 'system':
        return Icons.info;
      default:
        return Icons.notifications;
    }
  }

  Color _getPriorityColor(String priority) {
    switch (priority) {
      case 'high':
        return Colors.red;
      case 'medium':
        return Colors.orange;
      case 'low':
        return Colors.green;
      default:
        return Colors.grey;
    }
  }

  String _formatTime(DateTime time) {
    final now = DateTime.now();
    final difference = now.difference(time);
    
    if (difference.inMinutes < 1) {
      return 'Just now';
    } else if (difference.inHours < 1) {
      return '${difference.inMinutes}m ago';
    } else if (difference.inDays < 1) {
      return '${difference.inHours}h ago';
    } else if (difference.inDays < 7) {
      return '${difference.inDays}d ago';
    } else {
      return DateFormat('MMM d').format(time);
    }
  }

  void _handleNotificationTap(NotificationItem notification) {
    // Handle different notification types
    switch (notification.type) {
      case 'fatigue_alert':
        // Navigate to fatigue details
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Fatigue alert: ${notification.message}'),
            backgroundColor: Colors.orange,
          ),
        );
        break;
      case 'productivity_alert':
        // Navigate to productivity insights
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Productivity alert: ${notification.message}'),
            backgroundColor: Colors.blue,
          ),
        );
        break;
      case 'recommendation':
        // Show recommendation details
        showDialog(
          context: context,
          builder: (context) => AlertDialog(
            title: const Text('Recommendation'),
            content: Text(notification.message),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('Dismiss'),
              ),
              TextButton(
                onPressed: () {
                  Navigator.pop(context);
                  // Implement recommendation action
                },
                child: const Text('Apply'),
              ),
            ],
          ),
        );
        break;
    }
  }
}

// Notification item model
class NotificationItem {
  final String id;
  final String title;
  final String message;
  final String type;
  final String priority;
  final DateTime timestamp;
  final bool read;
  final Map<String, dynamic>? data;

  NotificationItem({
    required this.id,
    required this.title,
    required this.message,
    required this.type,
    required this.priority,
    required this.timestamp,
    this.read = false,
    this.data,
  });
}