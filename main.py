from fastapi import FastAPI, Form, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from datetime import datetime
import random, io, os
import pandas as pd
LOGO = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAZABkAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAC0AUADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD1eiiivyU9gKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKT/PWj/PWgQtFJ/nrR/nrQAtFJ/nrR/nrQAtFJ/nrR/nrQAtFJ/nrR/nrQMWik/wA9aP8APWgBaKT/AD1o/wA9aAFopM/T86Mj1H50CuLRSZHqPzoyPUfnQFxaKTI9R+dGR6j86AuLRTcj1H50Z9xQFxaKTPvRmgLi0UmaM/T86AuLRSZHqPzoyPUfnQFxaKTI9R+dGR6j86AuLRSZHqPzpMj1H50CuOopuR6j86Mj1H50BcdRTcj1H50ZHqPzoC47/PSgf54puR6j86UfhQFx1FJ/npR/npQMTP8AnNGf85pv4H/vmj8D/wB80ibi5NGaT8D+VH4H8qAuLk0ZNNz/AJxSZ/zigVx+TRk0zNLn/OKAuOyaMmm5/wA4pM/5xQFx+TRk0zP+cUmfp+VAXJNx96Nx96jz9Pyo/L8qAuSbj70ZPvUefpRn6UBzEmT70ZPvUefpRn6UBzEmT70ZPvUefpRn6UBzD8n3oyfemZ+lGfpQK4/J96Mn3pmR/kUflQO4/J96Mn3pmfpRke35UBcfk+9GT70zP+cUZoFcfk+9GT70zP8AnFH+elAXH5PvRk+/50z/AD0oByO34CgLj8n3/OjJ9/zpmR7flRn/ADigLj8n3/OjJ9/zpmf84oyP8igLj8n3/OgH3pmR7flTgff9cUDTHZ+lGfpSZ9//AB6jPv8A+PUDuN4/2f1o4/2f1oyfU/8AfdGT6n/vumSHH+z+tHHt+tGT6n/vujJ9T/31QAnHtSflS/if++qP89aQhPyo/Kg/55pKAF/KikooELRn2pKKAFopjOEBLbiB12qSf0qP7XF3Sfv/AMsX7fhVxpzlrFXJc4x3difPtRn2qH7XFn7k/XH+qf8AwpPtkWPuT/8Afl//AImn7Gp/K/uF7Wn/ADInz7UVAbuH+5P3/wCWL/8AxNH2uLP3J+uP9U/+FHsan8r+4Pa0/wCZE+fajPtUH2yLH3J/+/L/AOFH2yL+5P3/AOWT/wCFP2NT+V/cHtaf8yJ8+1FQ/a4s42T9cf6p/wDCk+2RY+5P/wB+X/8AiaXsan8r+4Pa0/5kTfjS1B9sj/uz/wDfl+3XtTkuI3baFlBH96Nh/MUOlUWri/uBVYPRSRL+FJ+NGaZJMsa7mDngn5ULHj2A/SoSbdkU2luSfjRVFtUgDY2XfUD/AI85T1HrtqeC7jnA2LMCf78Lp/6EBWsqFWKvKLS9GSqsG7Jompc0hoFYli5oB6VmX97JbvhHZflVuNPmn5zjqn8uo69KrHVLgZ/fPgF+mj3B6fj/APtdq64YOc4qS/KX6IydWztb8v8AM280ufb9axBqdxvA85/vKP8AkEXHcZ65/Xt0PNPt9RnkeMPK+0puO7S54x1PdjgfQ8/nVPA1Er/pL/5EXtktWvxX+ZsH8KTvmoXvbWIASXUStkD5nA5PQYzVc63pgGf7SssYzzOvrj1rCOHrS+GLfyZftYdy9+VPGf8AIzWadc0wZ/4mVhxn/l4Tt1qRNY0xzj+0bInIGBOpPP41X1Wv/I/uYKrT7l/n3/75owfQ/wDfIqvHe2U2PKurd88/K+f61MORkBcevNZShKLtJWNIzjLZ3+YEken5Um4+35UUVAXDcfb8qNx9vyoooFcM/T8qM/T8qKKAEzRRRQAUUUUAFFFFAEc8CXEbRuZAGxkxyMh4OeqkEVTOjWpz+9vud3/L/P36/wAf5enbFFFawrVIK0JNejJcU90L/Y9sGz5t9nIP/H9N2GP7/wCn403+xbULjzb/ABgD/j/n7HP9/wDX8KKKr61X/nf3sOSPYU6NanP72+53f8v8/fr/AB/l6dsUv9j2obPm32cg/wDH9N2GP7/6UUUfWq/87+9hyR7Df7FtQuPNv8YA/wCP+fsc/wB/9fwpTo1qc/vb7nd/y/z9+v8AH+Xp2xRRR9ar/wA7+9hyR7C/2PbBs+bfZyD/AMf03YY/v/p+NN/sW12482/xgD/j/n7HP9/9aKKPrVf+d/ew5I9hTo1qc/vb7nd/y/z9+v8AH+Xp2xUsOnQW7l0e6JIA+e6lcfkzEUUUniazVnN/ew5I9i31qnNpsE5JeS6Gd33LuVOvX7rD8PTtRRUQqTg7wbXoNxT3QwaPahg3m32Qwb/j+m6gY/v9Pbv1pY9Jtoiu2S8O0YG69mb88tzRRWn1mv8Azv72S4Re6LwGFAHQevNFFFYllS402C5bdJJdA4C/u7qWMcHPRWHPvUTaPbNn97fDO7pfTD73X+P8vTtiiitY4islZTf3slwj2F/si2zkS3oO4N/x/Tdhjpv6e3fr1qBdCWN1aHU9TjKgA3JkGD0yHznHqefXNFFenltWdSbjOTa89TjxSUWrE/9n3W4H+2b7AIONkPYdP8AV9+tNGnXW3H9t35O0DOyDPBzn/V9T0/+vzRRXsvC0P5F9yGpy017CnT7o5/4nN8M7uiQ8Z6f8s+3b9c1LHptyTn+2b/G4HG2HGAMY/1fQ9f5YHFFFR9Wo2+BfcgU5W36P8xy6XdAAHXNQOFAyVg556/6vr2qxDaSxn5765l5/jCD+SiiisMbh6MaLcYpfJCnOXtEr9T/2Q=="
USE_DB = True
try:
    from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
    from sqlalchemy.orm import declarative_base, sessionmaker
    DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql+psycopg2://fiberone:CHANGE_ME@127.0.0.1:5432/fiberone_noc")
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    Base = declarative_base()
    class POP(Base):
        __tablename__ = "pops"
        id = Column(Integer, primary_key=True)
        name = Column(String, unique=True)
        rect_count = Column(Integer)
        ip = Column(String)
        dc = Column(Float)
        load_a = Column(Float)
        mains = Column(Float)
        batt = Column(Float)
        kw = Column(Float)
        temp = Column(Float)
        soc = Column(Integer)
        status = Column(String)
        last_update = Column(DateTime, default=datetime.now)
    class User(Base):
        __tablename__ = "users"
        id = Column(Integer, primary_key=True)
        username = Column(String, unique=True)
        password = Column(String)
        role = Column(String)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    if db.query(User).count()==0:
        db.add(User(username="FiberOnenoc", password="FiberOne123", role="admin"))
        db.commit()
    POP_DEFS = [("Allen",2),("Alimosho",1),("Ojodu",2),("Ahmaddiya",1),("Surulere",2),("Gbagada",2),("Ogombo",1),("Ketu",2),("Ibadan Cocoa house",1),("Asokoro",1),("Jabi",1),("Abuja MAO Close",2),("Karsana Abuja",1),("Lokogoma",1),("Adewole Ilorin",1),("Lugbe",1),("Kubwa",1),("Kaura",1),("Malete",1),("Tanke",1),("Enekah",1),("Bodija Ibadan",1),("Ilasa/Parkland",1),("Orchid",2),("Sangotedo",2),("Agungi",2),("Cruise Plaza",2),("Anthony",2),("Arepo",2),("Festac/Amuwo",2),("Apapa",2),("Satellite Town",1),("Owode Ikorodu",1),("Ebate Ikorodu",1),("New Yaba",2),("VI",2),("Bookshop",1),("Lekki HQ",2),("Fleet Plaza",1)]
    if db.query(POP).count()==0:
        import random as _r
        for i,(name,rect) in enumerate(POP_DEFS):
            st=_r.choices(["OK","Minor","Major","Critical"],weights=[70,15,10,5])[0]
            dc=round(_r.uniform(52.8,54.5),2); load=round(_r.uniform(20 if rect==1 else 40, 60 if rect==1 else 110),1); mains=round(_r.uniform(210,238),1); batt=round(_r.uniform(-2.5,8),1); kw=round(dc*load/1000,2); temp=round(_r.uniform(24,60),1); soc=_r.randint(13,100)
            db.add(POP(name=name, rect_count=rect, ip=f"192.168.20.{100+i}", dc=dc, load_a=load, mains=mains, batt=batt, kw=kw, temp=temp, soc=soc, status=st))
        db.commit()
    db.close()
except Exception as e:
    print(f"DB fallback {e}"); USE_DB=False
app=FastAPI()
def get_pops():
    if USE_DB:
        db=SessionLocal(); pops=db.query(POP).all(); result=[{"id":f"{p.id:03d}","name":p.name,"rect":p.rect_count,"ip":p.ip,"dc":p.dc,"load":p.load_a,"mains":p.mains,"batt":p.batt,"kw":p.kw,"temp":p.temp,"soc":p.soc,"status":p.status} for p in pops]; db.close(); return result
    return []
def css(): return "<style>body{margin:0;font-family:sans-serif;background:#f3f5f9}.top{display:flex;align-items:center;gap:12px;padding:8px 14px;background:#fff;border-bottom:1px solid #e5e7eb;position:sticky;top:0}.ov{background:#1e40af;color:#fff;border:none;padding:5px 10px;border-radius:6px;font-size:12px}.pill{padding:4px 10px;border-radius:999px;font-size:11px;font-weight:700;color:#fff}.live{background:#16a34a}.m6{display:grid;grid-template-columns:repeat(6,1fr);gap:10px;padding:10px}.mc{background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:12px;text-align:center}.mc small{color:#6b7280;font-size:11px;display:block}.mc b{font-size:18px;display:block}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(360px,1fr));gap:10px;padding:10px}.card{background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:10px;border-left:4px solid #22c55e}.card.critical{border-left-color:#ef4444}.card.major{border-left-color:#f97316}.card.minor{border-left-color:#eab308}.head{display:flex;justify-content:space-between}.title{font-weight:800;font-size:13px}.sub{font-size:10px;color:#6b7280}.badge{color:#fff;font-size:10px;padding:4px 8px;border-radius:6px;font-weight:800}.ok{background:#22c55e}.minor{background:#eab308}.major{background:#f97316}.critical{background:#ef4444}.stats{display:grid;grid-template-columns:repeat(6,1fr);gap:4px;margin-top:8px}.stats div{text-align:center}.stats small{font-size:8px;color:#6b7280;display:block}.stats b{font-size:11px}.kpirow{display:grid;grid-template-columns:repeat(7,1fr);gap:8px;padding:10px}.kpi{background:#fff;border:1px solid #e5e7eb;border-radius:8px;padding:10px}.kpi small{font-size:10px;color:#6b7280}.kpi b{font-size:16px;display:block}.btn{padding:6px 12px;border-radius:6px;font-size:12px;border:1px solid #e5e7eb;background:#fff;text-decoration:none}.btn-blue{background:#1e40af;color:#fff;border:none}</style>"
def topbar(): return f"<div class=top><img src='{LOGO}' style='height:32px'><b>FiberOne NOC - 39 POPs | PostgreSQL</b> <a href='/dashboard'><button class=ov>6 METRICS</button></a> <a href='/export/excel' class=btn>📊 Excel</a> <div style='margin-left:auto;display:flex;gap:6px'><span class='pill live'>LIVE</span><a href='/logout' class=btn>Logout</a></div></div>" + css()
def check_auth(request: Request): return request.cookies.get("auth")=="ok"
@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return RedirectResponse("/dashboard") if check_auth(request) else RedirectResponse("/login")
@app.get("/login", response_class=HTMLResponse)
def login_page():
    return HTMLResponse(f"<html><head>{css()}</head><body style='display:flex;justify-content:center;align-items:center;height:100vh;background:#f3f5f9'><div style='background:#fff;padding:32px;border-radius:16px;width:400px;text-align:center;border:1px solid #e5e7eb;box-shadow:0 4px 12px rgba(0,0,0,0.08)'><img src='{LOGO}' style='height:52px;margin-bottom:12px'><div style='font-size:14px;font-weight:800;color:#1e3a8a'>FiberOne Rectifier NOC</div><div style='font-size:11px;color:#6b7280;margin-top:4px'>39 POPs REAL | 56 Rectifiers | PostgreSQL + Excel</div><form method=post action='/login' style='margin-top:20px'><input name=username placeholder='Username' value='FiberOnenoc' style='width:100%;padding:12px;margin:6px 0;border:1px solid #e5e7eb;border-radius:8px'><input name=password type=password placeholder='Password' value='FiberOne123' style='width:100%;padding:12px;margin:6px 0;border:1px solid #e5e7eb;border-radius:8px'><button style='width:100%;padding:12px;background:#1e40af;color:#fff;border:none;border-radius:8px;margin-top:10px;font-weight:700'>Login to NOC</button></form></div></body></html>")
@app.post("/login")
def do_login(response: Response, username: str = Form(...), password: str = Form(...)):
    valid=False
    if USE_DB:
        db=SessionLocal(); u=db.query(User).filter(User.username==username, User.password==password).first(); db.close(); valid=u is not None
    else:
        valid=(username=="FiberOnenoc" and password=="FiberOne123")
    if valid:
        resp=RedirectResponse("/dashboard",302); resp.set_cookie("auth","ok",httponly=True,max_age=86400); resp.set_cookie("user",username); return resp
    return HTMLResponse("<h3 style='color:red;text-align:center'>Login Failed</h3><a href='/login'>Try again</a>")
@app.get("/logout")
def logout():
    resp=RedirectResponse("/login",302); resp.delete_cookie("auth"); return resp
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    if not check_auth(request): return RedirectResponse("/login")
    pops=get_pops()
    if not pops: return HTMLResponse("DB empty, run DROP TABLE and restart")
    avg_dc=round(sum(p["dc"] for p in pops)/len(pops),2); total_load=round(sum(p["load"] for p in pops),1); avg_mains=round(sum(p["mains"] for p in pops)/len(pops),1); total_batt=round(sum(p["batt"] for p in pops),1); total_kw=round(sum(p["kw"] for p in pops),2); avg_temp=round(sum(p["temp"] for p in pops)/len(pops),1)
    cards="".join([f"<a href='/site/{p['id']}'><div class='card {p['status'].lower()}'><div class=head><div><div class=title>{p['name']} - {p['rect']} Rect</div><div class=sub>{p['ip']} | {p['status']}</div></div><span class='badge {p['status'].lower()}'>{p['status']}</span></div><div class=stats><div><small>DC V</small><b>{p['dc']} V</b></div><div><small>Load A</small><b>{p['load']} A</b></div><div><small>Mains</small><b>{p['mains']} V</b></div><div><small>Batt A</small><b>{p['batt']} A</b></div><div><small>kW</small><b>{p['kw']} kW</b></div><div><small>Temp</small><b>{p['temp']} C</b></div></div></div></a>" for p in pops])
    return HTMLResponse(f"<html><head>{topbar()}</head><body><div class=m6><div class=mc><small>DC Output Voltage</small><b>{avg_dc} V</b></div><div class=mc><small>Total Load Current</small><b>{total_load} A</b></div><div class=mc><small>Mains Supply</small><b>{avg_mains} V</b></div><div class=mc><small>Total Battery Current</small><b>{total_batt} A</b></div><div class=mc><small>Total Load Power</small><b>{total_kw} kW</b></div><div class=mc><small>Temperature</small><b>{avg_temp} C</b></div></div><div class=grid>{cards}</div></body></html>")
@app.get("/export/excel")
def export_excel(request: Request):
    if not check_auth(request): return RedirectResponse("/login")
    pops=get_pops(); df=pd.DataFrame(pops); output=io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='39 POPs Status', index=False)
    output.seek(0)
    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": f"attachment; filename=FiberOne_NOC_{datetime.now().strftime('%Y-%m-%d')}.xlsx"})
