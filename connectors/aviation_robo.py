import requests
import time
import random
import uuid

def run_flight_flow():
    url = "http://localhost:3001/kernel/ragnarok"
    print("✈️ [OBSIDIA-AVIONICS] Initialisation du flux GPS Defense...")

    while True:
        # Simulation de télémétrie de vol
        payload = {
            "domain": "gps_defense_aviation", # <--- MODIFICATION ICI
            "state": {
                "flight_id": f"AF{random.randint(100, 999)}",
                "altitude": random.randint(30000, 35000),
                "ground_speed": random.randint(400, 500),
                "gps_status": "LOCKED",
                "satellites_count": random.randint(8, 12),
                "signal_noise_ratio": round(random.uniform(35.0, 45.0), 2),
                "is_spoofing_detected": False
            }
        }

        try:
            res = requests.post(url, json=payload, timeout=5)
            if res.status_code == 200:
                print(f"✅ [AERO] Flight {payload['state']['flight_id']} | Alt: {payload['state']['altitude']}ft | GPS: OK")
            else:
                print(f"⚠️ [AERO] Kernel Busy: {res.status_code}")
        except Exception as e:
            print(f"❌ [AERO] Connection Lost: {e}")

        time.sleep(4) 

if __name__ == "__main__":
    run_flight_flow()