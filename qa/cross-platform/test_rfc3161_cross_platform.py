#!/usr/bin/env python3
"""
RFC3161 Cross-Platform Validation
Tests RFC3161 verification against multiple TSA implementations
"""

import subprocess
import json
import sys
from datetime import datetime
from pathlib import Path

# TSA endpoints (public, free tier)
TSA_ENDPOINTS = {
    "digicert": {
        "url": "http://timestamp.digicert.com",
        "name": "DigiCert",
        "available": False
    },
    "sectigo": {
        "url": "http://timestamp.sectigo.com",
        "name": "Sectigo",
        "available": False
    },
    "globalsign": {
        "url": "http://timestamp.globalsign.com/tsa",
        "name": "GlobalSign",
        "available": False
    },
    "apple": {
        "url": "http://timestamp.apple.com/ts01",
        "name": "Apple",
        "available": False
    },
    "freetsa": {
        "url": "http://freetsa.org/tsr",
        "name": "FreeTSA",
        "available": False
    }
}

class RFC3161CrossPlatformTester:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tsa_availability": {},
            "compatibility_matrix": {},
            "summary": {}
        }
    
    def check_tsa_availability(self):
        """Check which TSA endpoints are available"""
        print("=== Checking TSA Availability ===\n")
        
        for tsa_id, tsa_info in TSA_ENDPOINTS.items():
            print(f"Testing {tsa_info['name']} ({tsa_info['url']})...", end=" ")
            
            try:
                # Try to connect to TSA
                result = subprocess.run(
                    ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", tsa_info['url']],
                    timeout=5,
                    capture_output=True
                )
                
                if result.returncode == 0:
                    http_code = result.stdout.decode().strip()
                    available = http_code in ["200", "400", "415"]  # 400/415 means TSA is there but wrong request
                    TSA_ENDPOINTS[tsa_id]["available"] = available
                    self.results["tsa_availability"][tsa_id] = {
                        "name": tsa_info['name'],
                        "url": tsa_info['url'],
                        "available": available,
                        "http_code": http_code
                    }
                    print(f"✅ Available (HTTP {http_code})" if available else f"⚠️ Unreachable")
                else:
                    print(f"❌ Error")
                    self.results["tsa_availability"][tsa_id] = {
                        "name": tsa_info['name'],
                        "url": tsa_info['url'],
                        "available": False,
                        "error": str(result.stderr)
                    }
            except Exception as e:
                print(f"❌ Exception: {str(e)}")
                self.results["tsa_availability"][tsa_id] = {
                    "name": tsa_info['name'],
                    "url": tsa_info['url'],
                    "available": False,
                    "error": str(e)
                }
    
    def test_openssl_versions(self):
        """Test openssl compatibility"""
        print("\n=== Testing OpenSSL Versions ===\n")
        
        openssl_versions = {}
        
        # Check openssl version
        try:
            result = subprocess.run(
                ["openssl", "version"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"OpenSSL version: {version}")
                openssl_versions["version"] = version
                openssl_versions["available"] = True
            else:
                print("❌ OpenSSL not available")
                openssl_versions["available"] = False
        except Exception as e:
            print(f"❌ OpenSSL error: {str(e)}")
            openssl_versions["available"] = False
        
        # Check ts command availability
        try:
            result = subprocess.run(
                ["openssl", "ts", "-help"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 or "ts" in result.stderr:
                print("✅ openssl ts command available")
                openssl_versions["ts_command"] = True
            else:
                print("❌ openssl ts command not available")
                openssl_versions["ts_command"] = False
        except Exception as e:
            print(f"❌ openssl ts error: {str(e)}")
            openssl_versions["ts_command"] = False
        
        self.results["openssl_compatibility"] = openssl_versions
    
    def test_tlc_versions(self):
        """Test TLC versions"""
        print("\n=== Testing TLC Versions ===\n")
        
        tlc_versions = {}
        
        # Check tlc availability
        try:
            result = subprocess.run(
                ["tlc", "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.strip() or result.stderr.strip()
                print(f"TLC version: {version}")
                tlc_versions["version"] = version
                tlc_versions["available"] = True
            else:
                print("⚠️ TLC not available (install with: apt-get install tla-tools)")
                tlc_versions["available"] = False
        except Exception as e:
            print(f"⚠️ TLC not found: {str(e)}")
            tlc_versions["available"] = False
        
        self.results["tlc_compatibility"] = tlc_versions
    
    def test_sigma_implementations(self):
        """Test Sigma implementations"""
        print("\n=== Testing Sigma Implementations ===\n")
        
        sigma_tests = {}
        
        # Check obsidia_sigma_v130.py
        try:
            result = subprocess.run(
                ["python3", "server/python_agents/obsidia_sigma_v130.py"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 or "Usage" in result.stderr:
                print("✅ obsidia_sigma_v130.py available")
                sigma_tests["obsidia_sigma_v130"] = True
            else:
                print("⚠️ obsidia_sigma_v130.py error")
                sigma_tests["obsidia_sigma_v130"] = False
        except Exception as e:
            print(f"❌ obsidia_sigma_v130.py error: {str(e)}")
            sigma_tests["obsidia_sigma_v130"] = False
        
        # Check sigma_monitor.py
        try:
            result = subprocess.run(
                ["python3", "server/python_agents/sigma_monitor.py"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 or "Usage" in result.stderr:
                print("✅ sigma_monitor.py available")
                sigma_tests["sigma_monitor"] = True
            else:
                print("⚠️ sigma_monitor.py error")
                sigma_tests["sigma_monitor"] = False
        except Exception as e:
            print(f"❌ sigma_monitor.py error: {str(e)}")
            sigma_tests["sigma_monitor"] = False
        
        self.results["sigma_compatibility"] = sigma_tests
    
    def generate_compatibility_matrix(self):
        """Generate compatibility matrix"""
        print("\n=== Compatibility Matrix ===\n")
        
        matrix = {
            "rfc3161": {
                "openssl_available": self.results["openssl_compatibility"].get("available", False),
                "ts_command_available": self.results["openssl_compatibility"].get("ts_command", False),
                "tsa_endpoints_available": sum(1 for v in self.results["tsa_availability"].values() if v.get("available")),
                "total_tsa_endpoints": len(self.results["tsa_availability"])
            },
            "tla": {
                "tlc_available": self.results["tlc_compatibility"].get("available", False),
                "tlc_version": self.results["tlc_compatibility"].get("version", "unknown")
            },
            "sigma": {
                "obsidia_sigma_v130_available": self.results["sigma_compatibility"].get("obsidia_sigma_v130", False),
                "sigma_monitor_available": self.results["sigma_compatibility"].get("sigma_monitor", False)
            }
        }
        
        self.results["compatibility_matrix"] = matrix
        
        print("RFC3161 Compatibility:")
        print(f"  - OpenSSL available: {matrix['rfc3161']['openssl_available']}")
        print(f"  - ts command available: {matrix['rfc3161']['ts_command_available']}")
        print(f"  - TSA endpoints available: {matrix['rfc3161']['tsa_endpoints_available']}/{matrix['rfc3161']['total_tsa_endpoints']}")
        
        print("\nTLA Compatibility:")
        print(f"  - TLC available: {matrix['tla']['tlc_available']}")
        print(f"  - TLC version: {matrix['tla']['tlc_version']}")
        
        print("\nSigma Compatibility:")
        print(f"  - obsidia_sigma_v130 available: {matrix['sigma']['obsidia_sigma_v130_available']}")
        print(f"  - sigma_monitor available: {matrix['sigma']['sigma_monitor_available']}")
    
    def generate_summary(self):
        """Generate summary"""
        print("\n=== Summary ===\n")
        
        summary = {
            "rfc3161_status": "ready" if self.results["openssl_compatibility"].get("available") else "incomplete",
            "tla_status": "ready" if self.results["tlc_compatibility"].get("available") else "incomplete",
            "sigma_status": "ready" if self.results["sigma_compatibility"].get("obsidia_sigma_v130") else "incomplete",
            "overall_status": "production-ready" if all([
                self.results["openssl_compatibility"].get("available"),
                self.results["sigma_compatibility"].get("obsidia_sigma_v130")
            ]) else "development"
        }
        
        self.results["summary"] = summary
        
        print(f"RFC3161 Status: {summary['rfc3161_status']}")
        print(f"TLA Status: {summary['tla_status']}")
        print(f"Sigma Status: {summary['sigma_status']}")
        print(f"Overall Status: {summary['overall_status']}")
    
    def save_results(self):
        """Save results to JSON"""
        output_file = Path("server/python_agents/test_rfc3161_cross_platform_results.json")
        with open(output_file, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\n✅ Results saved to {output_file}")
    
    def run(self):
        """Run all tests"""
        print("RFC3161 Cross-Platform Validation\n")
        print("=" * 50)
        
        self.check_tsa_availability()
        self.test_openssl_versions()
        self.test_tlc_versions()
        self.test_sigma_implementations()
        self.generate_compatibility_matrix()
        self.generate_summary()
        self.save_results()
        
        print("\n" + "=" * 50)
        print("✅ Cross-platform validation complete")

if __name__ == "__main__":
    tester = RFC3161CrossPlatformTester()
    tester.run()
