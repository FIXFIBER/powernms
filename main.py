from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from datetime import datetime
import threading, time
from pysnmp.hlapi import *
from pops_config import POPS
from battery_logic import get_status, voltage_to_percent

app = FastAPI(title="FiberOne PowerNMS - powernms.fob.net.ng")

DATA = {} # ip -> live data
OID_VOLTAGE = "1.3.6.1.4.1.2011.6.122.15.1.2.1.5.1" # Huawei
COMMUNITY = "public"

def snmp_get(ip):
    try:
        iterator = getCmd(SnmpEngine(), CommunityData(COMMUNITY),
            UdpTransportTarget((ip, 161), timeout=2, retries=0),
            ContextData(), ObjectType(ObjectIdentity(OID_VOLTAGE)))
        errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
        if errorIndication or errorStatus: return 0
        return float(varBinds[0][1]) / 10.0
    except:
        return 0

def poller():
    while True:
        for p in POPS:
            v = snmp_get(p["ip"])
            is_live = v > 5 # If >5V, it's really LIVE
            percent = voltage_to_percent(v) if is_live else 0
            status = get_status(percent, is_live, v)

            DATA[p["ip"]] = {
                "pop_name": f"{p['pop']} {p['rectifier']}",
                "real_ip": p["ip"],
                "region": p["region"],
                "dc_voltage": v,
                "battery_percent": percent,
                "is_live": is_live,
                "status": status,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }
            print(f"{p['ip']} {v}V {'LIVE' if is_live else 'DOWN'}")
        time.sleep(60) # Every 60 sec 

@app.on_event("startup")
def start():
    t = threading.Thread(target=poller, daemon=True)
    t.start()

@app.get("/api/pops")
def api_pops():
    result = []
    for p in POPS:
        if p["ip"] in DATA:
            result.append(DATA[p["ip"]])
        else:
            # Not yet polled = DOWN till on network
            result.append({
                "pop_name": f"{p['pop']} {p['rectifier']}",
                "real_ip": p["ip"],
                "region": p["region"],
                "dc_voltage": 0,
                "battery_percent": 0,
                "is_live": False,
                "status": get_status(0, False, 0),
                "timestamp": "DOWN"
            })
    return result

@app.get("/api/stats")
def api_stats():
    vals = list(DATA.values())
    return {
        "total": 55,
        "green": len([x for x in vals if x["status"]["colour"]=="GREEN"]),
        "yellow": len([x for x in vals if x["status"]["colour"]=="YELLOW"]),
        "orange": len([x for x in vals if x["status"]["colour"]=="ORANGE"]),
        "red": len([x for x in vals if x["status"]["colour"]=="RED"]),
        "grey": 55 - len([x for x in vals if x["is_live"]])
    }

@app.get("/", response_class=HTMLResponse)
def frontend():
    return """
<!DOCTYPE html>
<html><head><title>FiberOne PowerNMS - powernms.fob.net.ng</title>
<script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-gray-100 p-4">
<div class="flex justify-between"><h1 class="text-xl font-bold">FiberOne PowerNMS <span class="text-sm text-gray-500">powernms.fob.net.ng</span></h1><div class="text-xs">55 POPs | 192.168.20.105-159 | LIVE + Real IP - No SIM</div></div>

<div class="grid grid-cols-5 gap-2 mt-3 text-[11px]">
<div class="bg-red-600 text-white p-2 rounded">🔴 CRITICAL - RED<br><20% | <2hrs<br>URGENT - Gen needed</div>
<div class="bg-orange-500 text-white p-2 rounded">🟠 LOW - ORANGE<br>20-39% | 2-4hrs<br>Monitor</div>
<div class="bg-yellow-400 p-2 rounded">🟡 WARNING - YELLOW<br>40-69% | 4-12hrs<br>OK</div>
<div class="bg-green-600 text-white p-2 rounded">🟢 LIVE OK - GREEN<br>70-100% | >12hrs<br>Normal</div>
<div class="bg-gray-400 text-white p-2 rounded">⚫ OFFLINE - GREY<br>No SNMP / No ping<br>Down till on network</div>
</div>

<div class="flex gap-2 mt-3 text-xs"><button onclick="setFilter('ALL')" class="px-3 py-1 bg-black text-white rounded">ALL</button>
<button onclick="setFilter('RED')" class="px-2 py-1 bg-white border rounded">RED</button>
<button onclick="setFilter('ORANGE')" class="px-2 py-1 bg-white border rounded">ORANGE</button>
<button onclick="setFilter('YELLOW')" class="px-2 py-1 bg-white border rounded">YELLOW</button>
<button onclick="setFilter('GREEN')" class="px-2 py-1 bg-white border rounded">GREEN</button>
<button onclick="setFilter('GREY')" class="px-2 py-1 bg-white border rounded">GREY/DOWN</button>
<span id="stats" class="ml-4 font-bold"></span><span id="time" class="ml-auto text-gray-500"></span></div>

<div id="grid" class="grid grid-cols-4 gap-3 mt-4"></div>

<script>
let pops=[], filter='ALL';
async function load(){let r=await fetch('/api/pops'); pops=await r.json(); let s=await fetch('/api/stats'); let st=await s.json(); document.getElementById('stats').innerHTML=`Total 55 | 🔴${st.red} 🟠${st.orange} 🟡${st.yellow} 🟢${st.green} ⚫${st.grey} DOWN`; document.getElementById('time').innerHTML=new Date().toLocaleTimeString(); render();}
function setFilter(f){filter=f; render();}
function render(){let grid=document.getElementById('grid'); grid.innerHTML=''; let list=filter==='ALL'?pops:pops.filter(p=>p.status.colour===filter); list.forEach(p=>{let d=document.createElement('div'); d.className=`rounded-lg p-3 border-2 ${p.status.css}`; d.innerHTML=`<div class="flex justify-between"><b class="text-sm">${p.pop_name}</b><span class="text-[10px]">${p.is_live?'LIVE':'DOWN'}</span></div><div class="text-xs">${p.real_ip} - ${p.region}</div><div class="text-xl font-bold mt-1">${p.battery_percent}% | ${p.dc_voltage}V</div><div class="text-xs">${p.status.icon} ${p.status.label} | ${p.status.backup}</div><div class="text-[10px]">${p.status.action} - ${p.timestamp}</div>`; grid.appendChild(d);})}
load(); setInterval(load,60000);
</script></body></html>
    """
