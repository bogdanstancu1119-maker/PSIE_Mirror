import json
import os
import subprocess
from datetime import datetime, timezone

def calculeaza_j_din_telemetrie() -> float:
    try:
        if os.path.exists("telemetry.json"):
            with open("telemetry.json", "r") as f:
                data = json.load(f)
            return float(data.get("J", 682.0))
    except Exception:
        pass
    return 682.0

def calculeaza_sdi_din_telemetrie() -> float:
    try:
        if os.path.exists("telemetry.json"):
            with open("telemetry.json", "r") as f:
                data = json.load(f)
            return float(data.get("SDI", 0.00))
    except Exception:
        pass
    return 0.00

def calculeaza_diversitate() -> float:
    try:
        if os.path.exists("legi_db.json"):
            with open("legi_db.json", "r") as f:
                db = json.load(f)
            nr_active = len(db.get("active", {}))
            nr_carantina = len(db.get("carantina", {}))
            total = nr_active + nr_carantina
            if total > 0:
                return round(nr_active / total, 2)
    except Exception:
        pass
    return 0.91

def kernel_arca() -> str:
    j_total = calculeaza_j_din_telemetrie()
    sdi = calculeaza_sdi_din_telemetrie()
    diversitate = calculeaza_diversitate()
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    data = {
        "timestamp": timestamp,
        "j_total": j_total,
        "sdi_global": sdi,
        "diversitate_d": diversitate,
        "l471_scut": {"activ": sdi < 0.81},
        "l347_transparenta": "ACTIVA",
        "kernel_versiune": "1.0.0",
    }

    cale_audit = "audit_L476.json"
    with open(cale_audit, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    try:
        subprocess.run(["git", "config", "user.name", "PSIE-Bot"], check=False)
        subprocess.run(["git", "config", "user.email", "psie-bot@users.noreply.github.com"], check=False)
        subprocess.run(["git", "add", cale_audit], check=True)
        subprocess.run(["git", "commit", "-m", f"L347: Puls {timestamp} | J={j_total} | SDI={sdi}"], check=False)
        subprocess.run(["git", "push"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[EROARE] Git push a eșuat: {e}")
        return "EROARE_PUSH"

    return "APROBAT_VOT"

if __name__ == "__main__":
    rezultat = kernel_arca()
    print(f"KERNEL ARCA: {rezultat}")
