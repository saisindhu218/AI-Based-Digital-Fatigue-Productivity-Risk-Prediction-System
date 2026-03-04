import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:fatigue_mobile_app/screens/splash_screen.dart';
import 'package:fatigue_mobile_app/providers/auth_provider.dart';
import 'package:fatigue_mobile_app/providers/usage_provider.dart';
import 'package:fatigue_mobile_app/providers/notification_provider.dart';

void main()async{

WidgetsFlutterBinding.ensureInitialized();

/* FIX 1: remove await initialize (not needed and causes errors) */

runApp(const AppInitializer());

}

/* FIX 2: separate initializer widget */

class AppInitializer extends StatelessWidget{

const AppInitializer({Key? key}):super(key:key);

@override
Widget build(BuildContext context){

return MultiProvider(

providers:[

ChangeNotifierProvider<AuthProvider>(
create:(_)=>AuthProvider()
),

ChangeNotifierProvider<UsageProvider>(
create:(_)=>UsageProvider()
),

ChangeNotifierProvider<NotificationProvider>(
create:(_)=>NotificationProvider()
),

],

child:const FatiguePredictionApp()

);

}

}

class FatiguePredictionApp extends StatelessWidget{

const FatiguePredictionApp({Key? key}):super(key:key);

@override
Widget build(BuildContext context){

return MaterialApp(

title:"FatigueGuard Mobile",

debugShowCheckedModeBanner:false,

theme:ThemeData(

primarySwatch:Colors.blue,

scaffoldBackgroundColor:const Color(0xFFF5F7FA),

appBarTheme:const AppBarTheme(
elevation:0,
backgroundColor:Colors.white,
iconTheme:IconThemeData(color:Colors.black),
titleTextStyle:TextStyle(
color:Colors.black,
fontSize:20,
fontWeight:FontWeight.w600
)
),

cardTheme:CardTheme(
elevation:2,
shape:RoundedRectangleBorder(
borderRadius:BorderRadius.circular(12)
)
)

),

home:const SplashScreen()

);

}

}