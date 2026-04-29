import sqlite3
import json

conn = sqlite3.connect("education_ai.db")
cursor = conn.cursor()
cursor.execute("SELECT id, topic, difficulty, image_paths, created_at FROM notes ORDER BY created_at DESC")
rows = cursor.fetchall()

print(f"\n{'─'*70}")
print(f"{'ID':<5} {'TOPIC':<30} {'LEVEL':<14} {'IMAGES':<8} {'DATE'}")
print(f"{'─'*70}")
for row in rows:
    id_, topic, diff, imgs, ts = row
    img_count = len(json.loads(imgs)) if imgs else 0
    print(f"{id_:<5} {str(topic)[:29]:<30} {str(diff or '—'):<14} {img_count:<8} {str(ts)[:10]}")
print(f"{'─'*70}")
print(f"Total: {len(rows)} topics\n")
conn.close()