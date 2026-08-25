import os
import zlib
import base64
import marshal
from pathlib import Path

def obfuscate_code(source_code):
    compiled = compile(source_code, "<string>", "exec")
    marshalled = marshal.dumps(compiled)
    compressed = zlib.compress(marshalled)
    b64 = base64.b64encode(compressed).decode("ascii")
    
    wrapper = (
        "import base64, zlib, marshal\n"
        f"exec(marshal.loads(zlib.decompress(base64.b64decode('{b64}'))))\n"
    )
    return wrapper

def process_directory(target_dir):
    py_files = [
        "run_local_automation.py",
        "content-publishing/devto_engagement_bot.py",
        "content-publishing/publish_zyvop_cloud.py",
        "content-publishing/save_zyvop_session.py",
        "github-outreach/fresh_java_growth_engine.py"
    ]
    
    for rel_path in py_files:
        full_path = Path(target_dir) / rel_path
        if full_path.exists():
            print(f"Obfuscating & Encrypting Code Logic: {rel_path}...")
            source = full_path.read_text(encoding="utf-8")
            if "marshal.loads" not in source:
                obfuscated = obfuscate_code(source)
                full_path.write_text(obfuscated, encoding="utf-8")
                print(f"  [ENCRYPTED] {rel_path} is now 100% obfuscated bytecode payload.")

if __name__ == "__main__":
    base_dir = Path(__file__).parent
    process_directory(base_dir)
