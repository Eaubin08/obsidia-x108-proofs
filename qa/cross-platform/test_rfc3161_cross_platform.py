#!/usr/bin/env python3
"""RFC3161 / TLC / Sigma cross-platform validation - P1 public"""

import json
import os
import subprocess
import sys
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

TSA_ENDPOINTS = {
    "digicert":   {"url": "http://timestamp.digicert.com",       "name": "DigiCert"},
    "sectigo":    {"url": "http://timestamp.sectigo.com",        "name": "Sectigo"},
    "globalsign": {"url": "http://timestamp.globalsign.com/tsa", "name": "GlobalSign"},
    "freetsa":    {"url": "http://freetsa.org/tsr",              "name": "FreeTSA"},
}

def _env():
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONWARNINGS"] = "ignore"
    return env

def _request_probe(url: str, method: str, timeout: int = 10):
    req = urllib.request.Request(
        url,
        method=method,
        headers={
            "User-Agent": "Obsidia-X108-QA/1.0",
            "Accept": "*/*",
            "Connection": "close",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            code = getattr(resp, "status", 200)
            return True, str(code), method
    except urllib.error.HTTPError as e:
        code = getattr(e, "code", None)
        ok = code in (200, 400, 403, 404, 405, 415)
        return ok, str(code), method
    except Exception as e:
        return False, str(e), method

def probe_url(url: str):
    ok, code, method = _request_probe(url, "HEAD", timeout=10)
    if ok:
        return True, code, method

    ok2, code2, method2 = _request_probe(url, "GET", timeout=10)
    if ok2:
        return True, code2, method2

    return False, f"HEAD={code} ; GET={code2}", "HEAD->GET"

class P1CrossPlatformTester:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "rfc3161_local": {},
            "rfc3161_network": {},
            "tlc": {},
            "sigma": {},
            "summary": {}
        }

    def test_rfc3161_local(self):
        print("=== RFC3161 Local (openssl) ===")
        r = {}
        try:
            res = subprocess.run(
                ["openssl", "version"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=5,
                env=_env(),
            )
            r["openssl_available"] = res.returncode == 0
            r["openssl_version"] = res.stdout.strip() if res.returncode == 0 else (res.stderr or "").strip()
        except Exception as e:
            r["openssl_available"] = False
            r["openssl_version"] = str(e)

        try:
            res = subprocess.run(
                ["openssl", "ts", "-help"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=5,
                env=_env(),
            )
            r["ts_command"] = (res.returncode == 0) or ("ts" in (res.stderr or ""))
        except Exception:
            r["ts_command"] = False

        print(f"  openssl: {r.get('openssl_version', 'N/A')}")
        print(f"  openssl ts: {r.get('ts_command', False)}")
        self.results["rfc3161_local"] = r

    def test_rfc3161_network(self):
        print("=== RFC3161 Reseau (TSA endpoints) ===")
        available = 0
        for tsa_id, info in TSA_ENDPOINTS.items():
            ok, code, method = probe_url(info["url"])
            self.results["rfc3161_network"][tsa_id] = {
                "name": info["name"],
                "available": ok,
                "http_code_or_error": code,
                "probe_method": method,
            }
            if ok:
                available += 1
            print(f"  {info['name']}: {'OK' if ok else 'UNREACHABLE'} ({code}) via {method}")
        self.results["rfc3161_network"]["_count_available"] = available

    def test_tlc(self):
        print("=== TLC (via tla2tools.jar) ===")
        jar_candidates = []
        if "USERPROFILE" in os.environ:
            jar_candidates.append(Path(os.environ["USERPROFILE"]) / "tla2tools.jar")
        jar_candidates.extend([
            Path.home() / "tla2tools.jar",
            ROOT / "tla2tools.jar",
        ])
        env_jar = os.environ.get("TLC_JAR")
        if env_jar:
            jar_candidates.insert(0, Path(env_jar))

        jar = next((p for p in jar_candidates if p.exists()), None)
        r = {"jar_found": bool(jar), "jar_path": str(jar) if jar else None}

        if not jar:
            r["available"] = False
            print("  tla2tools.jar not found")
        else:
            try:
                res = subprocess.run(
                    ["java", "-jar", str(jar), "-help"],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=10,
                    env=_env(),
                )
                r["available"] = (res.returncode == 0) or ("TLC" in ((res.stdout or "") + (res.stderr or "")))
                print(f"  tla2tools.jar: {'OK' if r['available'] else 'ERROR'} ({jar})")
            except Exception as e:
                r["available"] = False
                r["error"] = str(e)
                print(f"  java error: {e}")

        self.results["tlc"] = r

    def test_sigma(self):
        print("=== Sigma Public (sigma/) ===")
        sigma_dir = ROOT / "sigma"
        s = {"sigma_dir_exists": sigma_dir.exists()}

        required = ["run_pipeline.py", "sigma_monitor.py", "sigma_config.json", "contracts.py"]
        for fname in required:
            s[fname] = (sigma_dir / fname).exists()
            print(f"  {fname}: {'OK' if s[fname] else 'MISSING'}")

        try:
            proc = subprocess.run(
                [sys.executable, str(sigma_dir / "run_pipeline.py"), "bank", str(sigma_dir / "examples" / "bank_normal.json")],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=20,
                env=_env(),
            )
            s["run_pipeline_exitcode"] = proc.returncode
            s["run_pipeline_smoke"] = proc.returncode == 0
            if proc.returncode != 0:
                s["run_pipeline_error"] = proc.stderr.strip()
            print(f"  run_pipeline smoke: {'OK' if s['run_pipeline_smoke'] else 'FAIL'}")
        except Exception as e:
            s["run_pipeline_smoke"] = False
            s["run_pipeline_error"] = str(e)
            print(f"  run_pipeline smoke: EXCEPTION {e}")

        try:
            proc = subprocess.run(
                [sys.executable, str(sigma_dir / "sigma_monitor.py"), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=20,
                env=_env(),
            )
            s["sigma_monitor_exitcode"] = proc.returncode
            s["sigma_monitor_smoke"] = proc.returncode == 0
            if proc.returncode != 0:
                s["sigma_monitor_error"] = proc.stderr.strip()
            print(f"  sigma_monitor smoke: {'OK' if s['sigma_monitor_smoke'] else 'FAIL'}")
        except Exception as e:
            s["sigma_monitor_smoke"] = False
            s["sigma_monitor_error"] = str(e)
            print(f"  sigma_monitor smoke: EXCEPTION {e}")

        self.results["sigma"] = s

    def generate_summary(self):
        print("=== Resume P1 ===")
        local = self.results["rfc3161_local"]
        network = self.results["rfc3161_network"]
        tlc = self.results["tlc"]
        sigma = self.results["sigma"]

        summary = {
            "rfc3161_local": "PASS" if (local.get("openssl_available") and local.get("ts_command")) else "KNOWN_LIMIT",
            "rfc3161_network": f"{network.get('_count_available', 0)}/{len(TSA_ENDPOINTS)} TSA joignables",
            "tlc_via_jar": "PASS" if tlc.get("available") else "KNOWN_LIMIT (jar not installed or not detected)",
            "sigma_public": "PASS" if (sigma.get("run_pipeline_smoke") and sigma.get("sigma_monitor_smoke")) else "INCOMPLETE",
            "scope": "P1 PUBLIC - no global production-ready claim"
        }
        self.results["summary"] = summary
        for k, v in summary.items():
            print(f"  {k}: {v}")

    def save_results(self):
        out = ROOT / "qa" / "cross-platform" / "rfc3161_cross_platform_results.json"
        out.write_text(json.dumps(self.results, indent=2, ensure_ascii=True), encoding="utf-8")
        print(f"  Results: {out}")

    def run(self):
        print("RFC3161 / TLC / Sigma - Cross-Platform P1")
        print("=" * 50)
        self.test_rfc3161_local()
        self.test_rfc3161_network()
        self.test_tlc()
        self.test_sigma()
        self.generate_summary()
        self.save_results()
        print("=" * 50)
        print("Validation complete")

if __name__ == "__main__":
    P1CrossPlatformTester().run()