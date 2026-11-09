from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from datetime import datetime
import threading, time, subprocess, re
from pops_config import POPS
from battery_logic import get_status, voltage_to_percent

app = FastAPI(title="FiberOne PowerNMS")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://power.fob.net.ng", "http://power.fob.net.ng", "https://fixfiber.github.io", "http://localhost", "http://127.0.0.1"],
    allow_origin_regex=r"https://.*\.github\.io",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA = {}
OID_VOLTAGE = "1.3.6.1.4.1.2011.6.122.15.1.2.1.5.1"
COMMUNITY = "public"

def snmp_get(ip):
    try:
        r = subprocess.run(
            ["snmpget", "-v2c", "-c", COMMUNITY, "-t", "2", "-r", "0", "-Oqv", ip, OID_VOLTAGE],
            capture_output=True, text=True, timeout=6
        )
        s = (r.stdout or "").strip().strip('"')
        if not s or "No Response" in r.stderr or "Timeout" in r.stderr or r.returncode != 0:
            return 0.0
        m = re.search(r"[-+]?\d*\.?\d+", s)
        if not m:
            return 0.0
        val = float(m.group(0))
        return val / 10.0
    except Exception:
        return 0.0

def poller():
    while True:
        for p in POPS:
            v = snmp_get(p["ip"])
            is_live = v > 5
            percent = voltage_to_percent(v) if is_live else 0
            status = get_status(percent, is_live, v)
            DATA[p["ip"]] = {
                "pop_name": f"{p['pop']} {p['rectifier']}",
                "real_ip": p["ip"],
                "region": p["region"],
                "dc_voltage": round(v, 2),
                "battery_percent": percent,
                "is_live": is_live,
                "status": status,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }
        time.sleep(60)

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
            result.append({
                "pop_name": f"{p['pop']} {p['rectifier']}",
                "real_ip": p["ip"],
                "region": p["region"],
                "dc_voltage": 0,
                "battery_percent": 0,
                "is_live": False,
                "status": get_status(0, False, 0),
                "timestamp": "PENDING"
            })
    return result

@app.get("/api/stats")
def api_stats():
    vals = list(DATA.values())
    return {
        "total": len(POPS),
        "green": len([x for x in vals if x["status"]["colour"]=="GREEN"]),
        "yellow": len([x for x in vals if x["status"]["colour"]=="YELLOW"]),
        "orange": len([x for x in vals if x["status"]["colour"]=="ORANGE"]),
        "red": len([x for x in vals if x["status"]["colour"]=="RED"]),
        "grey": len(POPS) - len([x for x in vals if x["is_live"]])
    }

@app.get("/health")
def health():
    return {"ok": True, "total": len(POPS), "polled": len(DATA)}

@app.get("/", response_class=HTMLResponse)
def frontend():
    return """<!DOCTYPE html>
<html><head><title>FiberOne PowerNMS</title><script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-gray-100 p-4"><div class="text-sm">API active. Use /api/pops and /api/stats.</div></body></html>"""
