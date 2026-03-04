const API_BASE="http://127.0.0.1:8000/api/v1";

document.addEventListener("DOMContentLoaded",async function(){
const token=localStorage.getItem("token");
if(!token){window.location.href="login.html";return;}

const nameBox=document.getElementById("userEmail");
if(nameBox)nameBox.textContent=localStorage.getItem("studentName")||"User";

initNavigation();
initQuickActions();
showSection("dashboard-home");

await initStats();
await initCharts();
startStatsPolling();
});

function initNavigation(){
document.querySelectorAll(".nav-link").forEach(link=>{
link.onclick=(e)=>{
e.preventDefault();
const id=link.getAttribute("href").replace("#","");
showSection(id);
document.querySelectorAll(".nav-link").forEach(x=>x.classList.remove("active"));
link.classList.add("active");
};
});
}

function showSection(id){
document.querySelectorAll(".page-section").forEach(s=>s.classList.remove("active"));
const target=document.getElementById(id);
if(target)target.classList.add("active");
}

async function fetchDashboardStats(){
try{
const token=localStorage.getItem("token");
const res=await fetch(`${API_BASE}/usage/user/${localStorage.getItem("userId")}/recent?hours=24`,{
headers:{Authorization:`Bearer ${token}`}
});
if(!res.ok)throw new Error("API error");
const data=await res.json();
const summary=data.summary||{};
const predictions=data.predictions||[];
let latestFatigue=0,latestProductivity=0;
if(predictions.length>0){
latestFatigue=predictions[0].fatigue_score||0;
latestProductivity=predictions[0].productivity_score||0;
}
return{
fatigueScore:latestFatigue,
productivityScore:latestProductivity,
screenTime:((summary.total_screen_time_minutes||0)/60).toFixed(1),
sessions:(data.laptop_usage?.length||0)+(data.mobile_usage?.length||0),
predictions:predictions
};
}catch(e){
console.error(e);
return{fatigueScore:0,productivityScore:0,screenTime:0,sessions:0,predictions:[]};
}
}

async function initStats(){
const stats=await fetchDashboardStats();
setText("fatigue-score",`${stats.fatigueScore}%`);
setText("screen-time",`${stats.screenTime}h`);
setText("sessions",stats.sessions);
window.latestStats=stats;
}

function setText(id,val){
const el=document.getElementById(id);
if(el)el.textContent=val;
}

async function initCharts(){
const stats=window.latestStats||await fetchDashboardStats();
createFatigueChart(stats.predictions||[]);
createProductivityChart(stats.predictions||[]);
createUsageChart();
}

function createFatigueChart(predictions){
const ctx=document.getElementById("fatigueChart");
if(!ctx)return;
const labels=[],values=[];
predictions.slice(0,7).reverse().forEach(p=>{
labels.push(new Date(p.timestamp).toLocaleDateString());
values.push(p.fatigue_score);
});
if(window.fatigueChart)window.fatigueChart.destroy();
window.fatigueChart=new Chart(ctx,{type:"line",data:{labels:labels,datasets:[{data:values}]},options:{responsive:true,maintainAspectRatio:false}});
}

function createProductivityChart(predictions){
const ctx=document.getElementById("productivityChart");
if(!ctx)return;
const labels=[],values=[];
predictions.slice(0,7).reverse().forEach(p=>{
labels.push(new Date(p.timestamp).toLocaleDateString());
values.push(p.productivity_score);
});
if(window.productivityChart)window.productivityChart.destroy();
window.productivityChart=new Chart(ctx,{type:"bar",data:{labels:labels,datasets:[{data:values}]},options:{responsive:true,maintainAspectRatio:false}});
}

async function createUsageChart(){
try{
const token=localStorage.getItem("token");
const res=await fetch(`${API_BASE}/usage/user/${localStorage.getItem("userId")}/recent?hours=24`,{
headers:{Authorization:`Bearer ${token}`}
});
const data=await res.json();
let work=0,social=0,other=0;
(data.laptop_usage||[]).forEach(x=>{
const cat=(x.app_category||"OTHER").toUpperCase();
if(cat==="HIGH")work++;
else if(cat==="MEDIUM")other++;
else social++;
});
const ctx=document.getElementById("usageChart");
if(!ctx)return;
if(window.usageChart)window.usageChart.destroy();
window.usageChart=new Chart(ctx,{type:"doughnut",data:{labels:["Work","Social","Other"],datasets:[{data:[work,social,other]}]},options:{responsive:true,maintainAspectRatio:false}});
}catch(e){console.error(e);}
}

function initQuickActions(){
document.querySelectorAll(".action-btn").forEach(btn=>{
btn.onclick=()=>{if(btn.dataset.action==="view-insights")showSection("analytics");if(btn.dataset.action==="pair-device")showSection("qr-pairing");};
});
}

let statsInterval;
function startStatsPolling(){
if(statsInterval)clearInterval(statsInterval);
statsInterval=setInterval(async()=>{
const active=document.querySelector(".page-section.active");
if(active&&active.id==="dashboard-home"){
await initStats();
await initCharts();
}
},60000);
}