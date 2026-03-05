import 'dart:math';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:fatigue_mobile_app/services/api_service.dart';
import 'package:fatigue_mobile_app/services/usage_collector.dart';

class UsageProvider with ChangeNotifier{

double _fatigueScore=0;
String _fatigueLevel="Low";
double _productivityLoss=0;
double _todayScreenTime=0;
int _notificationCount=0;
bool _laptopConnected=false;
bool _mobileConnected=false;
List<String> _recommendations=[];
List<double> _usageData=[];
bool _isLoading=false;
String? _error;

double get fatigueScore=>_fatigueScore;
String get fatigueLevel=>_fatigueLevel;
double get productivityLoss=>_productivityLoss;
double get todayScreenTime=>_todayScreenTime;
int get notificationCount=>_notificationCount;
bool get laptopConnected=>_laptopConnected;
bool get mobileConnected=>_mobileConnected;
List<String> get recommendations=>_recommendations;
List<double> get usageData=>_usageData;
bool get isLoading=>_isLoading;
String? get error=>_error;

final ApiService _api=ApiService();
final UsageCollector _collector=UsageCollector();

Future<void> loadDashboardData(BuildContext context)async{

if(_isLoading)return;

try{

_setLoading(true);
_error=null;

await _collector.initialize();
_collector.startCollection(context);

await _loadPredictions();
await _loadDeviceStatus();
await _loadScreenTime();

_generateUsageChart();
_generateRecommendations();

}catch(e){

_error=e.toString();

}finally{

_setLoading(false);

}

}

Future<void> _loadScreenTime()async{

try{

final prefs=await SharedPreferences.getInstance();

_todayScreenTime=(prefs.getDouble("today_screen_time")??0).toDouble();
_notificationCount=prefs.getInt("notification_count")??0;

}catch(_){

_todayScreenTime=0;
_notificationCount=0;

}

}

Future<void> _loadPredictions()async{

try{

final result=await _api.getPredictions();

final fatigue=result["fatigue"] is Map?result["fatigue"]:{};
final productivity=result["productivity"] is Map?result["productivity"]:{};

_fatigueScore=((fatigue["score"]??0) as num).toDouble();
_fatigueLevel=(fatigue["level"]??"Low").toString();
_productivityLoss=((productivity["loss_hours"]??0) as num).toDouble();

}catch(_){

_fatigueScore=0;
_fatigueLevel="Low";
_productivityLoss=0;

}

}

Future<void> _loadDeviceStatus()async{

try{

final status=await _api.getDeviceStatus();

_laptopConnected=status["laptop"]==true;
_mobileConnected=status["mobile"]!=false;

}catch(_){

_laptopConnected=false;
_mobileConnected=true;

}

}

void _generateUsageChart(){

final rand=Random();

final maxValue=_fatigueScore==0?50:_fatigueScore;

_usageData=List.generate(
7,
(i)=>rand.nextDouble()*maxValue
);

}

void _generateRecommendations(){

_recommendations=[];

if(_fatigueScore>=75){

_recommendations.addAll([
"Take a break immediately",
"Avoid continuous usage",
"Reduce night screen time"
]);

}else if(_fatigueScore>=50){

_recommendations.addAll([
"Take breaks every 45 minutes",
"Stretch and hydrate",
"Avoid multitasking"
]);

}else{

_recommendations.addAll([
"You are doing well",
"Maintain this routine"
]);

}

}

void _setLoading(bool value){

_isLoading=value;
notifyListeners();

}

Future<void> refresh(BuildContext context)async{

await loadDashboardData(context);

}

void clearError(){

_error=null;
notifyListeners();

}

}