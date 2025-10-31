import os
import json
from xxhash import xxh64

# --- Config ---
base_path_file = "Filepaths.txt"
containers_file = "Containers.txt"
output_file = "GeneratedAssetMap.json"

EXTENSIONS = [
#IMAGES
".png", 
".tga", 
".jpg", 
".jpeg", 
".dds",
".psd",
".bmp",
# MATERIALS
".mat",
".exr",
".physicMaterial", 
".compute",
".cube",
".shader",
".cloth",
".shadervariants",
#ANIMATIONS / MODELS
".fbx", 
".obj",
".anim",
".mesh",
#UNITY FILES
".unity",
".prefab", 
".asset", 
".playable",
#SPINE FILES
".atlas",
".skel",
".spine",
#DATA FILES
".bytes", 
".json", 
".txt",  
".dat",
".cs",
".otf",
".srt",
".csv",
".html",
#AUDIO / VIDEO
".pck",
".bnk",
".mp4",
".usm",
".mov",
#OTHER
".CustomPropertyUI",
".patch",
".diff",
".log",
]

# --- Load base paths ---
with open(base_path_file, "r", encoding="utf-8") as f:
    base_paths = [line.strip() for line in f if line.strip()]

# --- Load container IDs ---
with open(containers_file, "r", encoding="utf-8") as f:
    container_ids = {line.strip() for line in f if line.strip()}

# --- Generate hashes for all base paths ---
hash_map = {}
for base_path in base_paths:
    for ext in EXTENSIONS:
        file_path = base_path + ext
        file_hash = str(int(xxh64(file_path.lower().encode("utf-8")).hexdigest(), 16))
        hash_map[file_hash] = file_path

# --- Compare and collect matches ---
matches = {cid: hash_map[cid] for cid in container_ids if cid in hash_map}

# --- Sort matches alphabetically by file path ---
matches_sorted = dict(sorted(matches.items(), key=lambda item: item[1].lower()))

if os.path.exists(output_file):
    with open(output_file, "r", encoding="utf-8") as f:
        try:
            existing = json.load(f)
        except json.JSONDecodeError:
            existing = {}
else:
    existing = {}

existing.update(matches_sorted)

sorted_output = dict(sorted(existing.items(), key=lambda x: x[1].lower()))

# --- Save to JSON ---
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(sorted_output, f, indent=2, ensure_ascii=False)

print(f"✅ Found {len(matches_sorted)} matches (sorted alphabetically). Saved to {output_file}")
input("\nDone! Press Enter to close...")