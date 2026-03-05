import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:fatigue_mobile_app/providers/notification_provider.dart';
import 'package:fatigue_mobile_app/models/notification_item.dart';
import 'package:intl/intl.dart';

class NotificationsScreen extends StatefulWidget {
  const NotificationsScreen({Key? key}) : super(key: key);

  @override
  State<NotificationsScreen> createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends State<NotificationsScreen> {
  String _selectedFilter = "all";

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      Provider.of<NotificationProvider>(context, listen: false)
          .loadNotifications();
    });
  }

  @override
  Widget build(BuildContext context) {
    final provider = Provider.of<NotificationProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text("Notifications"),
        actions: [
          PopupMenuButton<String>(
            onSelected: (value) {
              setState(() => _selectedFilter = value);
            },
            itemBuilder: (context) => const [
              PopupMenuItem(value: "all", child: Text("All Notifications")),
              PopupMenuItem(value: "unread", child: Text("Unread Only")),
              PopupMenuItem(value: "alerts", child: Text("Alerts Only")),
            ],
          ),
          IconButton(
            icon: const Icon(Icons.check_all),
            onPressed: () async {
              await provider.markAllAsRead();
              if (!mounted) return;
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text("All notifications marked as read"),
                ),
              );
            },
          ),
        ],
      ),
      body: provider.isLoading
          ? const Center(child: CircularProgressIndicator())
          : _buildList(provider),
    );
  }

  Widget _buildList(NotificationProvider provider) {
    final List<NotificationItem> list =
        provider.notifications.where((n) {
      if (_selectedFilter == "unread") return !n.read;
      if (_selectedFilter == "alerts") return n.priority == "high";
      return true;
    }).toList();

    if (list.isEmpty) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.notifications_none, size: 80, color: Colors.grey),
            SizedBox(height: 16),
            Text("No notifications",
                style: TextStyle(fontSize: 18, color: Colors.grey)),
            SizedBox(height: 8),
            Text("You're all caught up!",
                style: TextStyle(color: Colors.grey)),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: () => provider.loadNotifications(),
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: list.length,
        itemBuilder: (context, index) {
          return _buildItem(list[index], provider);
        },
      ),
    );
  }

  Widget _buildItem(
      NotificationItem notification, NotificationProvider provider) {
    return Dismissible(
      key: ValueKey(notification.id),
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
          notification.read
              ? Icons.mark_email_unread
              : Icons.mark_email_read,
          color: Colors.white,
        ),
      ),
      confirmDismiss: (direction) async {
        if (direction == DismissDirection.endToStart) {
          if (notification.read) {
            await provider.markAsUnread(notification.id);
          } else {
            await provider.markAsRead(notification.id);
          }
          return false;
        } else {
          final result = await showDialog<bool>(
            context: context,
            builder: (context) => AlertDialog(
              title: const Text("Delete Notification"),
              content: const Text("Are you sure?"),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(context, false),
                  child: const Text("Cancel"),
                ),
                TextButton(
                  onPressed: () => Navigator.pop(context, true),
                  child: const Text("Delete",
                      style: TextStyle(color: Colors.red)),
                ),
              ],
            ),
          );

          if (result == true) {
            await provider.deleteNotification(notification.id);
            return true;
          }
          return false;
        }
      },
      child: Card(
        elevation: notification.read ? 0 : 2,
        shape:
            RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        child: ListTile(
          title: Text(notification.title),
          subtitle: Text(notification.message),
          trailing:
              Text(_formatTime(notification.timestamp)),
        ),
      ),
    );
  }

  String _formatTime(DateTime time) {
    final diff = DateTime.now().difference(time);
    if (diff.inMinutes < 1) return "Just now";
    if (diff.inHours < 1) return "${diff.inMinutes}m ago";
    if (diff.inDays < 1) return "${diff.inHours}h ago";
    if (diff.inDays < 7) return "${diff.inDays}d ago";
    return DateFormat("MMM d").format(time);
  }
}