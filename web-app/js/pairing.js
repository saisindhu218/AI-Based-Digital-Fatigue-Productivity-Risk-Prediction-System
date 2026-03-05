const API_BASE="http://127.0.0.1:8000/api/v1";

document.addEventListener('DOMContentLoaded',function(){

const pairingSection=document.getElementById('qr-pairing');
if(!pairingSection)return;

if(window.pairingObserverAttached)return;
window.pairingObserverAttached=true;

const observer=new MutationObserver((mutations)=>{

mutations.forEach((mutation)=>{

if(mutation.type==='attributes' && mutation.attributeName==='class'){

const section=mutation.target;

if(section.id==='qr-pairing' && section.classList.contains('active')){

if(!window.pairingInitialized){

window.pairingInitialized=true;
initializePairing();

}

}

}

});

});

observer.observe(pairingSection,{attributes:true});

});

async function initializePairing(){

await generateQRCode();
setupRefreshButton();
startDeviceStatusPolling();

}

function setupRefreshButton(){

const refreshBtn=document.getElementById('refreshQR');
if(!refreshBtn)return;

refreshBtn.onclick=generateQRCode;

}

async function generateQRCode(){

try{

const token=localStorage.getItem("token");

const res=await fetch(`${API_BASE}/pairing/generate`,{
method:"POST",
headers:{
"Authorization":`Bearer ${token}`
}
});

const data=await res.json();

const pairingToken=data.pairing_code;

const container=document.getElementById("qrcode");

container.innerHTML=`

<div style="
width:200px;
height:200px;
background:#f8f9fa;
display:flex;
align-items:center;
justify-content:center;
border:2px dashed #667eea;
border-radius:10px;
margin:20px auto;
">

<div style="text-align:center">

<div style="font-size:14px;color:#666">
Pairing Code
</div>

<div style="font-size:24px;font-weight:bold;color:#667eea">
${pairingToken}
</div>

</div>

</div>

`;

localStorage.setItem("pairingToken",pairingToken);

}catch(e){

console.error("Pairing error",e);

}

}

let pairingInterval;

function startDeviceStatusPolling(){

if(pairingInterval)return;

checkDeviceStatus();

pairingInterval=setInterval(checkDeviceStatus,10000);

}

async function checkDeviceStatus(){

try{

const token=localStorage.getItem("token");

const res=await fetch(`${API_BASE}/pairing/status`,{
headers:{Authorization:`Bearer ${token}`}
});

const data=await res.json();

updateDeviceStatusUI(data);

}catch(e){

console.error("Status check failed",e);

}

}

function updateDeviceStatusUI(status){

const laptop=document.querySelectorAll('.status-item')[0]?.children[1];
const mobile=document.querySelectorAll('.status-item')[1]?.children[1];
const lastSync=document.querySelectorAll('.status-item')[2]?.children[1];
const dataPoints=document.querySelectorAll('.status-item')[3]?.children[1];

if(laptop){

laptop.innerHTML=status.laptop
?'<i class="fas fa-check-circle"></i> Connected'
:'<i class="fas fa-times-circle"></i> Disconnected';

}

if(mobile){

mobile.innerHTML=status.mobile
?'<i class="fas fa-check-circle"></i> Connected'
:'<i class="fas fa-times-circle"></i> Disconnected';

}

if(lastSync)lastSync.textContent=status.last_synced||"--";

if(dataPoints)dataPoints.textContent=(status.data_points||0).toLocaleString();

}