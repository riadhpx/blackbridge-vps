import asyncio
import logging
import json
import os
import secrets
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import uvicorn

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("BlackBridge")

app = FastAPI()
CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f: 
            config = json.load(f)
            if "mappings" not in config: config["mappings"] = []
            return config
    return {"vps_ip": "", "secret_key": "", "mappings": []}

def save_config(config):
    with open(CONFIG_FILE, "w") as f: json.dump(config, f)

# State
tunnel_status = "Stopped"
stats = {"total_bytes": 0}
should_run = False

@app.get("/stop")
async def stop_tunnel():
    global should_run, tunnel_status
    should_run = False
    tunnel_status = "Stopped"
    return RedirectResponse(url="/", status_code=303)

@app.get("/start")
async def start_tunnel():
    global should_run
    should_run = True
    return RedirectResponse(url="/", status_code=303)

@app.post("/update")
async def update_settings(vps_ip: str = Form(...), secret_key: str = Form(...)):
    config = load_config()
    config["vps_ip"] = vps_ip
    config["secret_key"] = secret_key
    save_config(config)
    return RedirectResponse(url="/", status_code=303)

@app.post("/add_mapping")
async def add_mapping(vps_port: int = Form(...), local_port: int = Form(...)):
    config = load_config()
    # Check if vps_port already exists to avoid duplicates
    if not any(m['vps_port'] == vps_port for m in config.get("mappings", [])):
        config["mappings"].append({"vps_port": vps_port, "local_port": local_port})
        save_config(config)
    return RedirectResponse(url="/", status_code=303)

@app.get("/delete_mapping/{index}")
async def delete_mapping(index: int):
    config = load_config()
    if 0 <= index < len(config["mappings"]):
        config["mappings"].pop(index)
        save_config(config)
    return RedirectResponse(url="/", status_code=303)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    config = load_config()
    status_text = tunnel_status.upper()
    is_active = should_run
    
    # Dynamic styles based on state
    status_glow = "0 0 10px rgba(255,255,255,0.3)" if is_active and tunnel_status == "Connected" else "none"
    dot_color = "#fff" if is_active else "#333"
    
    # Toggle button state
    if is_active:
        btn_bg, btn_fg, btn_border = "#000", "#fff", "1px solid #fff"
    else:
        btn_bg, btn_fg, btn_border = "#111", "#fff", "1px solid #333"
    
    btn_text = "STOP TUNNEL" if is_active else "START TUNNEL"
    action = "/stop" if is_active else "/start"
    
    mapping_html = ""
    for i, m in enumerate(config.get("mappings", [])):
        mapping_html += f"""
        <div class="mapping-row">
            <span style="color:#eee;">{m['vps_port']} <span style="color:#444;">→</span> {m['local_port']}</span>
            <a href="/delete_mapping/{i}">[DEL]</a>
        </div>
        """
    if not mapping_html:
        mapping_html = '<div class="empty-state">NO ACTIVE ROUTES</div>'

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8"><title>TUNNEL CONTROL</title>
        <style>
            @keyframes pulse {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} 100% {{ opacity: 1; }} }}
            @keyframes slideIn {{ from {{ transform: translateY(5px); opacity: 0; }} to {{ transform: translateY(0); opacity: 1; }} }}
            
            body {{ font-family: monospace; background: #050505; color: #aaa; display: flex; justify-content: center; padding: 2rem; margin: 0; }}
            .container {{ width: 100%; max-width: 400px; border: 1px solid #1a1a1a; padding: 2.5rem; animation: slideIn 0.3s ease-out; }}
            
            h1 {{ font-size: 0.9rem; letter-spacing: 3px; margin: 0 0 2.5rem 0; color: #fff; border-bottom: 1px solid #1a1a1a; padding-bottom: 1rem; text-align: center; }}
            h2 {{ font-size: 0.7rem; margin-top: 2rem; margin-bottom: 1rem; color: #444; text-transform: uppercase; letter-spacing: 2px; }}
            
            .status-line {{ display: flex; align-items: center; gap: 10px; margin-bottom: 2.5rem; font-weight: bold; font-size: 0.7rem; color: #666; }}
            .dot {{ width: 5px; height: 5px; background: {dot_color}; box-shadow: {status_glow}; {"animation: pulse 2s infinite;" if is_active else ""} }}
            
            input {{ 
                width: 100%; padding: 0.8rem; background: #000; border: 1px solid #1a1a1a; color: #fff; 
                box-sizing: border-box; font-family: inherit; margin-bottom: 0.5rem; transition: all 0.2s;
            }}
            input:focus {{ outline: none; border-color: #444; background: #080808; }}
            label {{ font-size: 0.6rem; color: #333; display: block; margin-top: 1rem; text-transform: uppercase; }}
            
            .btn {{ 
                width: 100%; padding: 0.8rem; font-weight: bold; cursor: pointer; font-family: inherit; 
                transition: all 0.2s; text-transform: uppercase; letter-spacing: 1px; font-size: 0.8rem;
            }}
            .btn-white {{ background: #222; color: #fff; border: 1px solid #333; }}
            .btn-white:hover {{ background: #fff; color: #000; border-color: #fff; }}
            
            .btn-ghost {{ background: #000; color: #666; border: 1px solid #1a1a1a; }}
            .btn-ghost:hover {{ color: #fff; border-color: #444; }}
            
            .mapping-row {{ 
                display: flex; justify-content: space-between; align-items: center; 
                border-bottom: 1px solid #111; padding: 0.8rem 0; font-size: 0.85rem; 
            }}
            .mapping-row a {{ color: #333; text-decoration: none; font-size: 0.65rem; transition: color 0.2s; }}
            .mapping-row a:hover {{ color: #ff4444; }}
            
            .empty-state {{ color: #1a1a1a; font-size: 0.65rem; padding: 1.5rem 0; text-align: center; border: 1px dashed #111; }}

            .main-toggle {{ 
                margin-top: 3rem; background: {btn_bg}; color: {btn_fg}; 
                border: {btn_border};
            }}
            .main-toggle:hover {{ background: #fff; color: #000; border-color: #fff; }}
            
            .footer {{ margin-top: 2.5rem; font-size: 0.55rem; text-align: center; color: #1a1a1a; letter-spacing: 2px; text-transform: uppercase; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="status-line">
                <div class="dot"></div>
                <span>SYSTEM_{status_text}</span>
            </div>
            
            <h1>BLACKBRIDGE_v2</h1>
            
            <form action="/update" method="post">
                <label>VPS_ENDPOINT</label>
                <input type="text" name="vps_ip" value="{config['vps_ip']}" placeholder="IP_ADDR">
                <label>AUTH_SECRET</label>
                <input type="password" name="secret_key" value="{config['secret_key']}" placeholder="••••••••">
                <button type="submit" class="btn btn-ghost" style="margin-top: 0.5rem;">SYNC_CONFIG</button>
            </form>

            <h2>ACTIVE_ROUTING</h2>
            <div style="min-height: 50px;">
                {mapping_html}
            </div>
            
            <form action="/add_mapping" method="post" style="display:grid; grid-template-columns: 1fr 1fr; gap:0.75rem; margin-top: 1rem;">
                <div>
                    <label>VPS_PORT</label>
                    <input type="number" name="vps_port" placeholder="0000">
                </div>
                <div>
                    <label>LOCAL_PORT</label>
                    <input type="number" name="local_port" placeholder="0000">
                </div>
                <button type="submit" class="btn btn-white" style="grid-column: span 2;">APPEND_ROUTE</button>
            </form>

            <a href="{action}" style="text-decoration:none;">
                <button class="btn main-toggle">{btn_text}</button>
            </a>
            
            <div class="footer">
                TRAFFIC_LOG: {stats.get('total_bytes', 0) // 1024}KB // SESSION_ACTIVE: {str(is_active).upper()}
            </div>
        </div>
    </body>
    </html>
    """

async def relay(reader, writer):
    try:
        while True:
            data = await reader.read(16384)
            if not data: break
            writer.write(data)
            await writer.drain()
            stats["total_bytes"] += len(data)
    except: pass
    finally: writer.close()

async def open_data_session(vps_ip, session_id, local_port):
    try:
        logger.info(f"Opening data session for local port {local_port}")
        vps_reader, vps_writer = await asyncio.open_connection(vps_ip, 10002)
        vps_writer.write(f"{session_id}\n".encode())
        await vps_writer.drain()
        
        local_reader, local_writer = await asyncio.open_connection('127.0.0.1', local_port)
        await asyncio.gather(
            relay(vps_reader, local_writer),
            relay(local_reader, vps_writer)
        )
    except Exception as e:
        logger.error(f"Data session error: {e}")

async def tunnel_worker():
    global tunnel_status
    while True:
        if not should_run:
            tunnel_status = "Stopped"; await asyncio.sleep(1); continue
        
        config = load_config()
        if not config["vps_ip"] or not config["secret_key"]:
            tunnel_status = "Waiting Credentials"; await asyncio.sleep(2); continue
            
        try:
            tunnel_status = "Connecting..."
            # Build mappings string: vps_p,loc_p;vps_p,loc_p
            mapping_str = ";".join([f"{m['vps_port']},{m['local_port']}" for m in config.get("mappings", [])])
            handshake = f"{config['secret_key']}|{mapping_str}\n"

            reader, writer = await asyncio.open_connection(config["vps_ip"], 10000)
            writer.write(handshake.encode())
            await writer.drain()
            
            resp = await reader.readline()
            if b"AUTH_OK" in resp:
                tunnel_status = "Connected"
                logger.info("Tunnel Active. Mappings synchronized with VPS.")
                while should_run:
                    try:
                        # Wait for signals from VPS with 30s timeout
                        line = await asyncio.wait_for(reader.readline(), timeout=30.0)
                        if not line: break
                        msg = line.decode().strip()
                        if msg.startswith("REQ_DATA|"):
                            _, session_id, local_port = msg.split("|")
                            asyncio.create_task(open_data_session(config["vps_ip"], session_id, int(local_port)))
                    except asyncio.TimeoutError:
                        # Ping VPS to keep connection alive and detect ghosting
                        writer.write(b"\n")
                        await writer.drain()
            else:
                tunnel_status = "Auth Error"; writer.close(); await asyncio.sleep(5)
        except Exception as e:
            logger.error(f"Link error: {e}")
            tunnel_status = "Disconnected"; await asyncio.sleep(5)

async def main():
    await asyncio.gather(
        tunnel_worker(),
        uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=8001, log_level="error")).serve()
    )

if __name__ == "__main__":
    asyncio.run(main())
