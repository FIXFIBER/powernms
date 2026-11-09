def get_status(percent, is_live, voltage):
    # ⚫ OFFLINE - GREY - No SNMP / No ping
    if not is_live:
        return {"colour":"GREY","icon":"⚫","label":"OFFLINE","backup":"DOWN","action":"Down till on network","css":"bg-gray-400 text-white"}

    # 🔴 CRITICAL <20% | <2hrs
    if percent < 20:
        return {"colour":"RED","icon":"🔴","label":"CRITICAL","backup":"<2hrs","action":"URGENT - Gen needed","css":"bg-red-600 text-white"}
    # 🟠 LOW 20-39%
    if percent < 40:
        return {"colour":"ORANGE","icon":"🟠","label":"LOW","backup":"2-4hrs","action":"Monitor","css":"bg-orange-500 text-white"}
    # 🟡 WARNING 40-69%
    if percent < 70:
        return {"colour":"YELLOW","icon":"🟡","label":"WARNING","backup":"4-12hrs","action":"OK","css":"bg-yellow-400 text-black"}
    # 🟢 LIVE OK 70-100%
    return {"colour":"GREEN","icon":"🟢","label":"LIVE OK","backup":">12hrs","action":"Normal","css":"bg-green-600 text-white"}

def voltage_to_percent(v):
    if v >= 53.5: return 100
    if v >= 51: return 85
    if v >= 48.5: return 70
    if v >= 46.5: return 50
    if v >= 44.5: return 30
    if v >= 43.5: return 15
    if v > 0: return 5
    return 0