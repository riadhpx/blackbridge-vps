# BlackBridge Secure Tunnel

A minimalist, high-performance reverse tunnel system designed for dynamic port mapping without pre-configuration. Features a monochrome minimalist UI, secure authentication, and host-networking for instant deployment.

## 🏗️ Architecture

- **VPS Server (Python/FastAPI)**: Acts as the gateway. Runs in Docker using host-networking.
- **Local Client (Python/FastAPI)**: Bridge between your local apps and the VPS.
- **Control Link**: A persistent TCP socket for handshake and mapping synchronization.
- **Data Channels**: Dynamic socket pairs created on-demand for traffic relay.

## ✨ Features

- **Dynamic Mapping**: Add/Remove ports via UI without restarting any service.
- **Host Networking**: Direct port binding on VPS for zero-config Docker deployment.
- **Safety Lock**: Configurable min/max port ranges to prevent interference with system ports (like 80, 22, 443).
- **Minimalist UI**: Clean, monochrome dashboard with subtle animations.
- **Secure**: Password-protected dashboards and unique 16-character authentication keys.

## 🚀 Quick Start

### 1. VPS Setup (The Gateway)
The easiest way is to use the official Docker image. You can run it directly or use Docker Compose.

**Using Docker run:**
```bash
docker run -d --name blackbridge --network host tooco/blackbridge-vps
```

**Using Docker Compose:**
1. Navigate to the `vps/` folder.
2. Run:
   ```bash
   docker-compose up -d
   ```

3. Access the dashboard at `http://YOUR_VPS_IP:10001` to get your **Secret Key**.

### 2. Local Setup (The Bridge)
1. Navigate to the `local/` folder on your PC.
2. Run `pip install -r requirements.txt`.
3. Run `python local_client.py` or use the provided `.bat` file.
4. Access `http://localhost:8001` and enter your VPS IP and Secret Key.

## 🛡️ Security
- Dashboards are protected by management passwords (default: `admin123`).
- All tunnel connections require a dynamically generated `SECRET_KEY`.
- No sensitive data is hardcoded; configuration is stored in local `.json` files.

---
Created with ❤️ for simple, secure tunneling.
