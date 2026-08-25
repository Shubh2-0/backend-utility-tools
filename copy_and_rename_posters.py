import os
import shutil

src_dir = r"C:\Users\shubh\Downloads\poster"
dst_dir = r"c:\Users\shubh\OneDrive\Desktop\github\central-automation-engine\banners"

os.makedirs(dst_dir, exist_ok=True)

files = sorted([f for f in os.listdir(src_dir) if f.endswith(".png") or f.endswith(".jpg")])

target_names = [
    "banner_resilience4j.png",
    "banner_redis_caching.png",
    "banner_spring_gateway.png",
    "banner_postgres_locking.png",
    "banner_virtual_threads.png",
    "banner_opentelemetry.png",
    "banner_spring_security.png",
    "banner_outbox_pattern.png",
    "banner_kafka_tuning.png",
    "banner_hexagonal_architecture.png"
]

print("Processing and renaming 10 poster images from Downloads/poster...")

for idx, f in enumerate(files):
    if idx < len(target_names):
        src_path = os.path.join(src_dir, f)
        dst_name = target_names[idx]
        dst_path = os.path.join(dst_dir, dst_name)
        shutil.copy(src_path, dst_path)
        print(f"[{idx+1}/10] Copied & Renamed: {f} -> {dst_name}")

print("\nSUCCESS: All 10 Cover Banners organized and renamed into central-automation-engine/banners/!")
