import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ApiService{

static const String baseUrl="http://10.0.2.2:8000/api/v1";

Future<Map<String,dynamic>> login(String email,String password)async{

try{

final res=await http.post(
Uri.parse("$baseUrl/auth/login"),
headers:{"Content-Type":"application/json"},
body:jsonEncode({
"email":email,
"password":password
})
);

if(res.statusCode==200){

final data=jsonDecode(res.body);

final prefs=await SharedPreferences.getInstance();

await prefs.setString("auth_token",data["access_token"]);
await prefs.setString("user_id",data["user_id"]);

return{
"success":true,
"user_id":data["user_id"],
"token":data["access_token"]
};

}else{

final data=jsonDecode(res.body);

return{
"success":false,
"error":data["detail"]??"login failed"
};

}

}catch(e){

return{
"success":false,
"error":e.toString()
};

}
}

Future<Map<String,dynamic>> register(
String name,
String email,
String password
)async{

try{

final res=await http.post(
Uri.parse("$baseUrl/auth/register"),
headers:{"Content-Type":"application/json"},
body:jsonEncode({
"email":email,
"full_name":name,
"password":password
})
);

if(res.statusCode==200){
return{"success":true};
}

final data=jsonDecode(res.body);

return{
"success":false,
"error":data["detail"]??"register failed"
};

}catch(e){

return{
"success":false,
"error":e.toString()
};

}
}

Future<void> sendMobileUsage({
required String deviceId,
required String userId,
required Map<String,dynamic> usageData
})async{

try{

final prefs=await SharedPreferences.getInstance();

final token=prefs.getString("auth_token");

await http.post(
Uri.parse("$baseUrl/usage/mobile"),
headers:{
"Content-Type":"application/json",
if(token!=null)"Authorization":"Bearer $token"
},
body:jsonEncode({
"device_id":deviceId,
"user_id":userId,
"timestamp":usageData["timestamp"],
"session_id":usageData["session_id"],
"app_name":usageData["app_name"],
"screen_time":usageData["screen_time"],
"category":usageData["category"],
"notifications_received":usageData["notifications_received"]
})
);

}catch(e){

print("Usage send error: $e");

}
}

Future<Map<String,dynamic>> getPredictions()async{

try{

final prefs=await SharedPreferences.getInstance();

final token=prefs.getString("auth_token");
final userId=prefs.getString("user_id");

if(userId==null){
return _defaultPrediction();
}

final res=await http.post(
Uri.parse("$baseUrl/prediction/predict"),
headers:{
"Content-Type":"application/json",
if(token!=null)"Authorization":"Bearer $token"
},
body:jsonEncode({
"user_id":userId
})
);

if(res.statusCode==200){

return jsonDecode(res.body);

}

return _defaultPrediction();

}catch(e){

return _defaultPrediction();

}
}

Future<Map<String,dynamic>> getDeviceStatus()async{

try{

final prefs=await SharedPreferences.getInstance();

final token=prefs.getString("auth_token");
final userId=prefs.getString("user_id");

if(userId==null){
return {"laptop":false,"mobile":false};
}

final res=await http.get(
Uri.parse("$baseUrl/pairing/status/$userId"),
headers:{
if(token!=null)"Authorization":"Bearer $token"
}
);

if(res.statusCode==200){

return jsonDecode(res.body);

}

return {"laptop":false,"mobile":false};

}catch(e){

return {"laptop":false,"mobile":false};

}
}

Future<Map<String,String>> getHeaders()async{

final prefs=await SharedPreferences.getInstance();

final token=prefs.getString("auth_token");

return{
"Content-Type":"application/json",
if(token!=null)"Authorization":"Bearer $token"
};

}

Map<String,dynamic> _defaultPrediction(){

return{
"fatigue":{"score":0,"level":"Low"},
"productivity":{"loss_hours":0}
};

}

}