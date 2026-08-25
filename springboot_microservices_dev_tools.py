"""
Spring Boot Microservices Backend Developer Utility Suite
Author: Shubham Bhati (Backend Engineer)
"""

import sys
import json
import time
import urllib.request
import urllib.parse
from datetime import datetime

class SpringBootHealthMonitor:
    def __init__(self, endpoints=None):
        self.endpoints = endpoints or [
            "http://localhost:8080/actuator/health",
            "http://localhost:8081/actuator/health",
            "http://localhost:8082/actuator/health"
        ]

    def check_health(self):
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Spring Boot Actuator Health Check:")
        for ep in self.endpoints:
            try:
                req = urllib.request.Request(ep, headers={"User-Agent": "SpringBootDevTool/1.0"})
                with urllib.request.urlopen(req, timeout=3) as resp:
                    status_code = resp.getcode()
                    body = json.loads(resp.read().decode('utf-8'))
                    status = body.get("status", "UNKNOWN")
                    print(f"  [OK {status_code}] {ep} -> Status: {status}")
            except Exception as e:
                print(f"  [OFFLINE/DOWN] {ep} -> Error: {e}")

class JwtDebugInspector:
    @staticmethod
    def decode_jwt_payload(jwt_token):
        try:
            parts = jwt_token.split(".")
            if len(parts) != 3:
                return "Invalid JWT format. Expected 3 header.payload.signature parts."
            
            payload_b64 = parts[1]
            # Add padding
            payload_b64 += "=" * ((4 - len(payload_b64) % 4) % 4)
            import base64
            decoded_bytes = base64.urlsafe_b64decode(payload_b64)
            payload_json = json.loads(decoded_bytes.decode('utf-8'))
            return json.dumps(payload_json, indent=2)
        except Exception as e:
            return f"Error decoding JWT: {e}"

if __name__ == "__main__":
    print("=========================================================")
    print("   Spring Boot Backend Developer Utility CLI")
    print("=========================================================")
    monitor = SpringBootHealthMonitor()
    monitor.check_health()
    
    print("\nJWT Debug Inspector Test:")
    sample_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJTaHViaGFtQmhhdGkiLCJyb2xlcyI6WyJST0xFX0FETUlOIl0sImlhdCI6MTY3MjUxMTknMH0.sample_signature"
    print("Sample JWT Payload:")
    print(JwtDebugInspector.decode_jwt_payload(sample_jwt))
    print("=========================================================")
