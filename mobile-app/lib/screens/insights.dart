import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:fatigue_mobile_app/providers/usage_provider.dart';
import 'package:fatigue_mobile_app/widgets/stat_card.dart';

class InsightsScreen extends StatefulWidget{
const InsightsScreen({Key? key}) : super(key:key);

@override
State<InsightsScreen> createState()=>_InsightsScreenState();
}

class _InsightsScreenState extends State<InsightsScreen>{

int _selectedTimeRange=0;

final List<String> _timeRanges=["Today","Week","Month"];

@override
Widget build(BuildContext context){

final usageProvider=Provider.of<UsageProvider>(context);

return Scaffold(

appBar:AppBar(
title:const Text("Insights & Analytics"),
actions:[
IconButton(
icon:const Icon(Icons.refresh),
onPressed:usageProvider.isLoading
?null
:(){
usageProvider.refresh(context);
}
)
]
),

body:RefreshIndicator(

onRefresh:()async{
await usageProvider.refresh(context);
},

child:SingleChildScrollView(

padding:const EdgeInsets.all(16),

child:Column(

crossAxisAlignment:CrossAxisAlignment.start,

children:[

_buildTimeSelector(),

const SizedBox(height:20),

const Text(
"Productivity Overview",
style:TextStyle(
fontSize:18,
fontWeight:FontWeight.w600
)
),

const SizedBox(height:16),

_buildStats(),

const SizedBox(height:24),

_buildUsageChart(usageProvider),

const SizedBox(height:24),

_buildAppUsage(),

const SizedBox(height:24),

_buildProductivityHours(),

const SizedBox(height:40),

]

)

)

)

);

}

Widget _buildTimeSelector(){

return Row(

children:_timeRanges.asMap().entries.map((entry){

final index=entry.key;
final label=entry.value;

return Expanded(

child:Padding(

padding:const EdgeInsets.symmetric(horizontal:4),

child:ElevatedButton(

onPressed:(){

setState(()=>_selectedTimeRange=index);

},

style:ElevatedButton.styleFrom(

backgroundColor:_selectedTimeRange==index
?const Color(0xFF4A90E2)
:Colors.grey[300],

foregroundColor:_selectedTimeRange==index
?Colors.white
:Colors.black

),

child:Text(label)

)

)

);

}).toList()

);

}

Widget _buildStats(){

return GridView.count(

shrinkWrap:true,
physics:const NeverScrollableScrollPhysics(),

crossAxisCount:2,
crossAxisSpacing:12,
mainAxisSpacing:12,
childAspectRatio:1.2,

children:const[

StatCard(
title:"Focus Time",
value:"3.2",
subtitle:"hours today",
icon:Icons.timer,
color:Colors.green
),

StatCard(
title:"Distractions",
value:"18",
subtitle:"interruptions",
icon:Icons.notifications_active,
color:Colors.orange
),

StatCard(
title:"Task Complete",
value:"85%",
subtitle:"completion rate",
icon:Icons.check_circle,
color:Colors.blue
),

StatCard(
title:"Breaks Taken",
value:"7",
subtitle:"recommended breaks",
icon:Icons.coffee,
color:Colors.purple
),

]

);

}

Widget _buildUsageChart(UsageProvider provider){

final List<double> data=provider.usageData.isEmpty
?[10,20,30,40,50,60,70]
:provider.usageData;

return Card(

shape:RoundedRectangleBorder(
borderRadius:BorderRadius.circular(16)
),

child:Padding(

padding:const EdgeInsets.all(16),

child:Column(

crossAxisAlignment:CrossAxisAlignment.start,

children:[

const Text(
"Usage Trends",
style:TextStyle(
fontSize:18,
fontWeight:FontWeight.w600
)
),

const SizedBox(height:16),

SizedBox(

height:200,

child:LineChart(

LineChartData(

gridData:const FlGridData(show:true),

borderData:FlBorderData(show:false),

minX:0,
maxX:6,

minY:0,
maxY:100,

titlesData:FlTitlesData(

rightTitles:const AxisTitles(
sideTitles:SideTitles(showTitles:false)
),

topTitles:const AxisTitles(
sideTitles:SideTitles(showTitles:false)
),

bottomTitles:AxisTitles(

sideTitles:SideTitles(

showTitles:true,

getTitlesWidget:(value,meta){

const days=[
"Mon","Tue","Wed","Thu","Fri","Sat","Sun"
];

if(value.toInt()<days.length){

return Text(days[value.toInt()]);

}

return const Text("");

}

)

),

leftTitles:AxisTitles(

sideTitles:SideTitles(

showTitles:true,
interval:20,

getTitlesWidget:(value,meta){

return Text("${value.toInt()}%");

}

)

)

),

lineBarsData:[

LineChartBarData(

spots:data.asMap().entries.map(

(e)=>FlSpot(
e.key.toDouble(),
e.value.toDouble()
)

).toList(),

isCurved:true,

color:const Color(0xFF4A90E2),

barWidth:3,

belowBarData:BarAreaData(
show:true,
color:const Color(0xFF4A90E2).withOpacity(0.2)
)

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

Widget _buildAppUsage(){

final apps=[

{"name":"VS Code","time":"2.5h"},
{"name":"Chrome","time":"1.8h"},
{"name":"Slack","time":"1.2h"},
{"name":"WhatsApp","time":"45m"}

];

return Card(

shape:RoundedRectangleBorder(
borderRadius:BorderRadius.circular(16)
),

child:Padding(

padding:const EdgeInsets.all(16),

child:Column(

crossAxisAlignment:CrossAxisAlignment.start,

children:[

const Text(
"App Usage Breakdown",
style:TextStyle(
fontSize:18,
fontWeight:FontWeight.w600
)
),

const SizedBox(height:16),

...apps.map((app){

return Padding(

padding:const EdgeInsets.symmetric(vertical:6),

child:Row(

children:[

const Icon(Icons.apps),

const SizedBox(width:10),

Expanded(child:Text(app["name"]!)),

Text(app["time"]!)

]

)

);

})

]

)

)

);

}

Widget _buildProductivityHours(){

return Card(

shape:RoundedRectangleBorder(
borderRadius:BorderRadius.circular(16)
),

child:Padding(

padding:const EdgeInsets.all(16),

child:Column(

crossAxisAlignment:CrossAxisAlignment.start,

children:[

const Text(
"Peak Productivity Hours",
style:TextStyle(
fontSize:18,
fontWeight:FontWeight.w600
)
),

const SizedBox(height:12),

_buildHour("09:00 - 11:00","High",Colors.green),
_buildHour("11:00 - 13:00","Medium",Colors.orange),
_buildHour("13:00 - 15:00","Low",Colors.red)

]

)

)

);

}

Widget _buildHour(String time,String level,Color color){

return Padding(

padding:const EdgeInsets.symmetric(vertical:6),

child:Row(

children:[

Expanded(child:Text(time)),

Container(

padding:const EdgeInsets.symmetric(horizontal:10,vertical:4),

decoration:BoxDecoration(
color:color.withOpacity(0.2),
borderRadius:BorderRadius.circular(20)
),

child:Text(
level,
style:TextStyle(color:color)
)

)

]

)

);

}

}