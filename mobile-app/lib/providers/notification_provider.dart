import 'package:flutter/material.dart';
import 'package:fatigue_mobile_app/services/api_service.dart';
import 'package:fatigue_mobile_app/models/notification_item.dart';

class NotificationProvider with ChangeNotifier{

List<NotificationItem> _notifications=[];
bool _isLoading=false;
String? _error;

List<NotificationItem> get notifications=>_notifications;
bool get isLoading=>_isLoading;
String? get error=>_error;
int get unreadCount=>_notifications.where((n)=>!n.read).length;

final ApiService _apiService=ApiService();

static Future<void> initialize()async{}

Future<void> loadNotifications()async{

try{

_setLoading(true);
_error=null;

Map<String,dynamic> response;

try{

response=await _apiService.getNotifications();

}catch(_){

response={"success":false};

}

if(response["success"]==true){

final List list=response["notifications"]??[];

_notifications=list
.map((item)=>NotificationItem.fromJson(item))
.toList();

}else{

_loadMock();

}

notifyListeners();

}catch(e){

_error=e.toString();
_loadMock();

}finally{

_setLoading(false);

}

}

void _loadMock(){

_notifications=[

NotificationItem(
id:"1",
title:"Fatigue Alert",
message:"Fatigue level high. Take break.",
type:"fatigue_alert",
priority:"high",
timestamp:DateTime.now()
),

NotificationItem(
id:"2",
title:"Recommendation",
message:"Use Pomodoro technique.",
type:"recommendation",
priority:"medium",
timestamp:DateTime.now(),
read:true
)

];

}

Future<void> markAsRead(String id)async{

final index=_notifications.indexWhere((n)=>n.id==id);

if(index!=-1){

_notifications[index]=_notifications[index].copyWith(read:true);

notifyListeners();

}

}

Future<void> markAsUnread(String id)async{

final index=_notifications.indexWhere((n)=>n.id==id);

if(index!=-1){

_notifications[index]=_notifications[index].copyWith(read:false);

notifyListeners();

}

}

Future<void> markAllAsRead()async{

for(int i=0;i<_notifications.length;i++){

_notifications[i]=_notifications[i].copyWith(read:true);

}

notifyListeners();

}

Future<void> deleteNotification(String id)async{

_notifications.removeWhere((n)=>n.id==id);

notifyListeners();

}

void addNotification(NotificationItem notification){

_notifications.insert(0,notification);

notifyListeners();

}

void _setLoading(bool value){

_isLoading=value;
notifyListeners();

}

void clearError(){

_error=null;
notifyListeners();

}

}