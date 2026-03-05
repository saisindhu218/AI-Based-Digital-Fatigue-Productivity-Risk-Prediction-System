const API_BASE="http://127.0.0.1:8000/api/v1";

document.addEventListener('DOMContentLoaded',function(){

const analyticsSection=document.getElementById('analytics');
if(!analyticsSection)return;

if(window.analyticsObserverAttached)return;
window.analyticsObserverAttached=true;

const observer=new MutationObserver((mutations)=>{

mutations.forEach((mutation)=>{

if(mutation.type==='attributes' && mutation.attributeName==='class'){

const section=mutation.target;

if(section.id==='analytics' && section.classList.contains('active')){

if(!window.analyticsInitialized){

window.analyticsInitialized=true;
initializeAnalyticsCharts();

}

}

}

});

});

observer.observe(analyticsSection,{attributes:true});

});

async function initializeAnalyticsCharts(){

const data=await loadAnalyticsData();

createDailyUsageChart(data);
createWeeklyTrendsChart(data);
createAppUsageChart(data);
createFocusChart(data);

}

async function loadAnalyticsData(){

try{

const token=localStorage.getItem("token");
const userId=localStorage.getItem("userId");

const res=await fetch(`${API_BASE}/prediction/user/${userId}/history`,{
headers:{Authorization:`Bearer ${token}`}
});

const json=await res.json();

return json.predictions || [];

}catch(e){

console.error("Analytics API error",e);
return[];

}

}

function createDailyUsageChart(predictions){

const ctx=document.getElementById('dailyUsageChart');
if(!ctx)return;

const labels=[];
const screenData=[];
const productiveData=[];

predictions.slice(0,7).reverse().forEach(p=>{

labels.push(new Date(p.timestamp).toLocaleDateString());

screenData.push((p.productivity_score||0)/10);
productiveData.push((p.productivity_score||0)/12);

});

if(window.dailyUsageChart)window.dailyUsageChart.destroy();

window.dailyUsageChart=new Chart(ctx,{
type:'line',
data:{
labels:labels,
datasets:[
{
label:'Screen Time (hours)',
data:screenData,
borderColor:'#667eea',
backgroundColor:'rgba(102,126,234,0.1)',
tension:0.4,
fill:true
},
{
label:'Productive Time (hours)',
data:productiveData,
borderColor:'#10b981',
backgroundColor:'rgba(16,185,129,0.1)',
tension:0.4,
fill:true
}
]
},
options:{responsive:true,maintainAspectRatio:false}
});

}

function createWeeklyTrendsChart(predictions){

const ctx=document.getElementById('weeklyTrendsChart');
if(!ctx)return;

const labels=[];
const fatigue=[];
const productivity=[];

predictions.slice(0,7).reverse().forEach(p=>{

labels.push(new Date(p.timestamp).toLocaleDateString());
fatigue.push(p.fatigue_score);
productivity.push(p.productivity_score);

});

if(window.weeklyTrendsChart)window.weeklyTrendsChart.destroy();

window.weeklyTrendsChart=new Chart(ctx,{
type:'line',
data:{
labels:labels,
datasets:[
{
label:'Fatigue Score',
data:fatigue,
borderColor:'#ef4444',
backgroundColor:'rgba(239,68,68,0.1)',
fill:true,
tension:0.4
},
{
label:'Productivity Index',
data:productivity,
borderColor:'#667eea',
backgroundColor:'rgba(102,126,234,0.1)',
fill:true,
tension:0.4
}
]
},
options:{responsive:true,maintainAspectRatio:false}
});

}

async function createAppUsageChart(){

const token=localStorage.getItem("token");
const userId=localStorage.getItem("userId");

try{

const res=await fetch(`${API_BASE}/usage/user/${userId}/recent?hours=24`,{
headers:{Authorization:`Bearer ${token}`}
});

const data=await res.json();

let work=0;
let social=0;
let other=0;

(data.laptop_usage||[]).forEach(x=>{

const cat=(x.app_category||"OTHER").toUpperCase();

if(cat==="HIGH")work++;
else if(cat==="MEDIUM")other++;
else social++;

});

const ctx=document.getElementById('appUsageChart');
if(!ctx)return;

if(window.appUsageChart)window.appUsageChart.destroy();

window.appUsageChart=new Chart(ctx,{
type:'bar',
data:{
labels:['Work','Social','Other'],
datasets:[{
data:[work,social,other],
backgroundColor:['#667eea','#764ba2','#6b7280']
}]
},
options:{responsive:true,maintainAspectRatio:false}
});

}catch(e){

console.error("App usage chart error",e);

}

}

function createFocusChart(predictions){

const ctx=document.getElementById('focusChart');
if(!ctx)return;

let focused=0;
let distracted=0;
let breaks=0;

predictions.forEach(p=>{

if(p.fatigue_score<40)focused++;
else if(p.fatigue_score<70)distracted++;
else breaks++;

});

if(window.focusChart)window.focusChart.destroy();

window.focusChart=new Chart(ctx,{
type:'doughnut',
data:{
labels:['Focused','Distracted','Fatigue'],
datasets:[{
data:[focused,distracted,breaks],
backgroundColor:['#10b981','#f59e0b','#ef4444']
}]
},
options:{responsive:true,maintainAspectRatio:false,cutout:'70%'}
});

}