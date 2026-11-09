from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from datetime import datetime
import threading, time
from pysnmp.hlapi import *
from pops_config import POPS
from battery_logic import get_status, voltage_to_percent
app = FastAPI(title="FiberOne PowerNMS - power.fob.net.ng")
DATA = {}
OID_VOLTAGE = "1.3.6.1.4.1.2011.6.122.15.1.2.1.5.1"
COMMUNITY = "public"
def snmp_get(ip):
    try:
        iterator = getCmd(SnmpEngine(), CommunityData(COMMUNITY), UdpTransportTarget((ip, 161), timeout=2, retries=0), ContextData(), ObjectType(ObjectIdentity(OID_VOLTAGE)))
        err, _, _, varBinds = next(iterator)
        if err: return 0
        return float(varBinds[0][1]) / 10.0
    except: return 0
def poller():
    while True:
        for p in POPS:
            v = snmp_get(p["ip"])
            is_live = v > 5
            percent = voltage_to_percent(v) if is_live else 0
            DATA[p["ip"]] = {"pop_name": f"{p['pop']} {p['rectifier']}", "real_ip": p["ip"], "region": p["region"], "dc_voltage": v, "battery_percent": percent, "is_live": is_live, "status": get_status(percent, is_live, v), "timestamp": datetime.now().strftime("%H:%M:%S")}
        time.sleep(60)
@app.on_event("startup")
def start():
    t = threading.Thread(target=poller, daemon=True)
    t.start()
@app.get("/api/pops")
def api_pops():
    result=[]
    for p in POPS:
        result.append(DATA.get(p["ip"], {"pop_name": f"{p['pop']} {p['rectifier']}", "real_ip": p["ip"], "region": p["region"], "dc_voltage": 0, "battery_percent": 0, "is_live": False, "status": get_status(0, False, 0), "timestamp": "DOWN"}))
    return result
@app.get("/api/stats")
def api_stats():
    vals=list(DATA.values())
    return {"total":55,"green":len([x for x in vals if x["status"]["colour"]=="GREEN"]),"yellow":len([x for x in vals if x["status"]["colour"]=="YELLOW"]),"orange":len([x for x in vals if x["status"]["colour"]=="ORANGE"]),"red":len([x for x in vals if x["status"]["colour"]=="RED"]),"grey":55-len([x for x in vals if x["is_live"]])}
@app.get("/", response_class=HTMLResponse)
def frontend():
    return """<!DOCTYPE html><html><head><title>PowerNMS - power.fob.net.ng</title><script src="https://cdn.tailwindcss.com"></script></head><body class="bg-gray-100 p-4"><h1 class="text-xl font-bold">FiberOne PowerNMS - power.fob.net.ng - 55 POPs LIVE+Real IP No SIM</h1><div id="grid" class="grid grid-cols-4 gap-3 mt-4"></div><script>let pops=[];async function load(){let r=await fetch('/api/pops'); pops=await r.json(); let g=document.getElementById('grid'); g.innerHTML=''; pops.forEach(p=>{let d=document.createElement('div'); d.className=`rounded p-3 ${p.status.css}`; d.innerHTML=`<b>${p.pop_name}</b><br>${p.real_ip} - ${p.status.label} - ${p.battery_percent}% ${p.dc_voltage}V - ${p.is_live?'LIVE':'DOWN'}`; g.appendChild(d);})}load();setInterval(load,60000);</script></body></html>"""
