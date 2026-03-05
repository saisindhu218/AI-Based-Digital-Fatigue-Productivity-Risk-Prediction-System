import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:fatigue_mobile_app/providers/usage_provider.dart';
import 'package:fatigue_mobile_app/providers/auth_provider.dart';
import 'package:fatigue_mobile_app/widgets/stat_card.dart';
import 'package:fatigue_mobile_app/widgets/fatigue_meter.dart';

class Dashboard extends StatefulWidget{
const Dashboard({Key? key}) : super(key:key);

@override
State<Dashboard> createState()=>_DashboardState();
}

class _DashboardState extends State<Dashboard>{

@override
void initState(){
super.initState();
WidgetsBinding.instance.addPostFrameCallback((_){
_loadDashboard();
});
}

Future<void> _loadDashboard()async{
await Provider.of<UsageProvider>(context,listen:false)
.loadDashboardData(context);
}

@override
Widget build(BuildContext context){

final auth=Provider.of<AuthProvider>(context);
final usage=Provider.of<UsageProvider>(context);

return Scaffold(

appBar:AppBar(
title:const Text("Dashboard"),
actions:[
IconButton(
icon:const Icon(Icons.qr_code),
onPressed:()=>Navigator.pushNamed(context,"/qr-scanner")
),
IconButton(
icon:const Icon(Icons.notifications),
onPressed:()=>Navigator.pushNamed(context,"/notifications")
)
],
),

body:RefreshIndicator(
onRefresh:()=>usage.refresh(context),
child:SingleChildScrollView(
padding:const EdgeInsets.all(16),
child:Column(
crossAxisAlignment:CrossAxisAlignment.start,
children:[

_buildWelcome(auth.userName),

const SizedBox(height:20),

FatigueMeter(
fatigueScore:usage.fatigueScore,
fatigueLevel:usage.fatigueLevel
),

const SizedBox(height:20),

_buildStats(usage),

const SizedBox(height:20),

_buildChart(usage),

const SizedBox(height:20),

_buildRecommendations(usage),

const SizedBox(height:20),

_buildDeviceStatus(usage),

]
)
)
),

bottomNavigationBar:_bottomNav(context)

);
}

Widget _buildWelcome(String? name){

return Column(
crossAxisAlignment:CrossAxisAlignment.start,
children:[

Text(
"Hello, ${name??"User"}",
style:const TextStyle(
fontSize:24,
fontWeight:FontWeight.bold
)
),

const SizedBox(height:4),

Text(
"Your fatigue analytics overview",
style:TextStyle(
color:Colors.grey[600]
)
)

]
);

}

Widget _buildStats(UsageProvider p){

return GridView.count(
shrinkWrap:true,
physics:const NeverScrollableScrollPhysics(),
crossAxisCount:2,
crossAxisSpacing:12,
mainAxisSpacing:12,
childAspectRatio:1.2,
children:[

StatCard(
title:"Productivity Loss",
value:"${p.productivityLoss.toStringAsFixed(1)} h",
subtitle:"Today",
icon:Icons.trending_down,
color:Colors.orange
),

StatCard(
title:"Screen Time",
value:"${(p.todayScreenTime/60).toStringAsFixed(1)} h",
subtitle:"Today",
icon:Icons.phone_android,
color:Colors.blue
),

StatCard(
title:"Fatigue Score",
value:p.fatigueScore.toStringAsFixed(0),
subtitle:p.fatigueLevel,
icon:Icons.psychology,
color:Colors.red
),

StatCard(
title:"Notifications",
value:p.notificationCount.toString(),
subtitle:"Today",
icon:Icons.notifications,
color:Colors.purple
),

]
);

}

Widget _buildChart(UsageProvider p){

return Card(
child:Padding(
padding:const EdgeInsets.all(16),
child:Column(
crossAxisAlignment:CrossAxisAlignment.start,
children:[

const Text(
"Usage Trend",
style:TextStyle(
fontSize:18,
fontWeight:FontWeight.bold
)
),

const SizedBox(height:16),

SizedBox(
height:200,
child:LineChart(

LineChartData(
gridData:const FlGridData(show:false),
titlesData:const FlTitlesData(show:false),
borderData:FlBorderData(show:false),

lineBarsData:[

LineChartBarData(
spots:p.usageData
.asMap()
.entries
.map((e)=>FlSpot(
e.key.toDouble(),
e.value
))
.toList(),

isCurved:true,
color:Colors.blue,
barWidth:3
)

]

)

)

)

]
)
)
);

}

Widget _buildRecommendations(UsageProvider p){

return Card(
child:Padding(
padding:const EdgeInsets.all(16),
child:Column(
crossAxisAlignment:CrossAxisAlignment.start,
children:[

const Text(
"Recommendations",
style:TextStyle(
fontWeight:FontWeight.bold,
fontSize:18
)
),

const SizedBox(height:12),

...p.recommendations.map(
(e)=>Padding(
padding:const EdgeInsets.symmetric(vertical:4),
child:Row(
children:[

const Icon(Icons.check,color:Colors.green),

const SizedBox(width:8),

Expanded(child:Text(e))

]
)
)
)

]
)
)
);

}

Widget _buildDeviceStatus(UsageProvider p){

return Card(
child:Padding(
padding:const EdgeInsets.all(16),
child:Row(
children:[

_status("Laptop",p.laptopConnected),

const SizedBox(width:20),

_status("Mobile",p.mobileConnected)

]
)
)
);

}

Widget _status(String name,bool ok){

return Row(
children:[

Container(
width:10,
height:10,
decoration:BoxDecoration(
color:ok?Colors.green:Colors.red,
shape:BoxShape.circle
)
),

const SizedBox(width:8),

Text("$name ${ok?"Connected":"Disconnected"}")

]
);

}

Widget _bottomNav(BuildContext context){

return BottomNavigationBar(
currentIndex:0,
items:const[
BottomNavigationBarItem(
icon:Icon(Icons.dashboard),
label:"Dashboard"
),
BottomNavigationBarItem(
icon:Icon(Icons.insights),
label:"Insights"
),
BottomNavigationBarItem(
icon:Icon(Icons.settings),
label:"Settings"
)
],
onTap:(i){

if(i==1){
Navigator.pushNamed(context,"/insights");
}

if(i==2){
Navigator.pushNamed(context,"/settings");
}

}
);

}

}