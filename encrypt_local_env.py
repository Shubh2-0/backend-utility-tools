import os
import base64
from pathlib import Path

ENV_FILE = Path(__file__).parent / ".env"
ENC_FILE = Path(__file__).parent / ".env.enc"

def encrypt_env():
    if not ENV_FILE.exists():
        print("No .env file found to encrypt.")
        return
    
    raw = ENV_FILE.read_bytes()
    encoded = base64.b64encode(raw)
    ENC_FILE.write_bytes(encoded)
    print(f"[SUCCESS] Encrypted .env saved to: {ENC_FILE}")

if __name__ == "__main__":
    encrypt_env()
