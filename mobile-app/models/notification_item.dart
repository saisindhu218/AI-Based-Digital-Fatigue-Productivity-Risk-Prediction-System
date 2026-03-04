class NotificationItem{

final String id;
final String title;
final String message;
final String type;
final String priority;
final DateTime timestamp;
final bool read;
final Map<String,dynamic>? data;

const NotificationItem({

required this.id,
required this.title,
required this.message,
required this.type,
required this.priority,
required this.timestamp,
this.read=false,
this.data

});

NotificationItem copyWith({

bool? read,
String? title,
String? message,
String? type,
String? priority,
DateTime? timestamp,
Map<String,dynamic>? data

}){

return NotificationItem(

id:id,
title:title??this.title,
message:message??this.message,
type:type??this.type,
priority:priority??this.priority,
timestamp:timestamp??this.timestamp,
read:read??this.read,
data:data??this.data

);

}

factory NotificationItem.fromJson(Map<String,dynamic> json){

return NotificationItem(

id:(json["id"]??"").toString(),

title:(json["title"]??"").toString(),

message:(json["message"]??"").toString(),

type:(json["type"]??"system").toString(),

priority:(json["priority"]??"low").toString(),

timestamp:DateTime.tryParse(json["timestamp"]??"")??DateTime.now(),

read:json["read"]??false,

data:json["data"] is Map<String,dynamic>?json["data"]:null

);

}

Map<String,dynamic> toJson(){

return{

"id":id,
"title":title,
"message":message,
"type":type,
"priority":priority,
"timestamp":timestamp.toIso8601String(),
"read":read,
"data":data

};

}

}