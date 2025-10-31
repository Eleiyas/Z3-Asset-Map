import os
import json
import time
from xxhash import xxh64
from multiprocessing import Process, Queue, Event, cpu_count 
from datetime import timedelta
import atexit

# --- CONFIG --- #
FOLDER_FILE = "Folders/Common.txt"
FILENAMES_FILE = "Filenames/assets_map_Animator.txt"
CONTAINERS_FILE = "Containers/Containers.txt"

OUTPUT_FILE = "GeneratedAssetMap.json"

EXTENSIONS = [
#IMAGES
".png", 
".tga", 
".jpg", 
".jpeg", 
".dds",
".psd",
".bmp",
## MATERIALS
".mat",
#".exr",
#".physicMaterial", 
#".compute",
#".cube",
#".shader",
#".cloth",
#".shadervariants",
##ANIMATIONS / MODELS
".fbx", 
#".obj",
".anim",
".mesh",
##UNITY FILES
".unity",
".prefab", 
".asset", 
#".playable",
##SPINE FILES
#".atlas",
#".skel",
#".spine",
##DATA FILES
".bytes", 
".json", 
".txt",  
#".dat",
#".cs",
#".otf",
#".srt",
#".csv",
#".html",
##AUDIO / VIDEO
#".pck",
#".bnk",
#".mp4",
#".usm",
#".mov",
##OTHER
#".CustomPropertyUI",
#".patch",
#".diff",
#".log",
]

ROOTS = [
"Assets/OriginalResRepos/ART/Char/Bangboo/Bangboo_Sumoboo",
]

# Sets the depth of folders, filenames and extensions (Ex: Depth 3 = Root/1/2/3.ext)
MAX_DEPTH = 3

# --- PERFORMANCE TUNING --- #
WORKER_BATCH_SIZE = 10000
PROGRESS_INTERVAL_SECONDS = 5

# --- HELPERS --- #
def load_file_lines(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return {line.strip() for line in f if line.strip()}
    except FileNotFoundError:
        return set()

# --- FILEPATH GENERATOR --- #
def generate_candidates(folders, depth, max_depth, current_path, filenames, extensions):
    if depth == max_depth:
        for fn in filenames:
            for ext in extensions:
                yield f"{current_path}/{fn}{ext}"
        return
    for folder in folders:
        new_path = f"{current_path}/{folder}"
        yield from generate_candidates(folders, depth + 1, max_depth, new_path, filenames, extensions)
    for fn in filenames:
        for ext in extensions:
            yield f"{current_path}/{fn}{ext}"

# --- WORKER PROCESS --- #
def worker_task(base_root, folders, filenames, extensions, max_depth,
                container_ids, q, matches_q):
   
    count_buffer = 0
    for candidate in generate_candidates(folders, 1, max_depth, base_root, filenames, extensions):
        candidate_lower = candidate.lower()
        candidate_hash = xxh64(candidate_lower.encode("utf-8")).hexdigest()
            
        count_buffer += 1 
        
        file_hash_int = str(int(candidate_hash, 16))
        if file_hash_int in container_ids:
            print(f"[FOUND] {file_hash_int} -> {candidate}")
            matches_q.put((file_hash_int, candidate))

        if count_buffer >= WORKER_BATCH_SIZE:
            q.put(count_buffer)
            count_buffer = 0
            
    if count_buffer:
        q.put(count_buffer)
        
    print(f"Worker for {base_root} finished.")

# --- WRITER & REPORTER PROCESS --- #
def writer_reporter_process(q, matches_q, shutdown_flag): 
    """Handles writing to disk and reporting progress (COUNT-based)."""
    all_found_matches = {}
    total_tested_this_session = 0
    start_time = time.time()
    last_progress_time = time.time()
    
    atexit.register(final_save, matches_q, all_found_matches)
    
    print("\n--- Starting Search (press Ctrl+C to stop gracefully) ---")

    while not shutdown_flag.is_set():
        try:
            while not matches_q.empty():
                f_hash, f_path = matches_q.get_nowait()
                all_found_matches[f_hash] = f_path
            
            count_batch = q.get(timeout=0.5) 
            total_tested_this_session += count_batch 
            
        except Exception:
            pass
        
        now = time.time()
        if now - last_progress_time > PROGRESS_INTERVAL_SECONDS:
            elapsed = now - start_time
            speed = total_tested_this_session / elapsed if elapsed > 0 else 0
            print(f"[PROGRESS] Tested paths: {total_tested_this_session:,} | Speed: {speed:,.0f} paths/s | Found: {len(all_found_matches)}")
            last_progress_time = now

    print("[IO] Shutdown signal received.")
    
    while not q.empty():
        try:
            total_tested_this_session += q.get_nowait()
        except Exception:
            break
            
    print(f"[IO] Final total tested this session: {total_tested_this_session:,}")


# --- FINAL SAVE LOGIC --- #
def final_save(matches_q, existing_matches):
    while not matches_q.empty():
        f_hash, f_path = matches_q.get_nowait()
        existing_matches[f_hash] = f_path
    if not existing_matches:
        print("\nNo new matches found in this session.")
        return
    print(f"\n--- Saving {len(existing_matches)} total matches from this session... ---")

    initial_filenames = load_file_lines(FILENAMES_FILE)
    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            disk_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        disk_data = {}
    disk_data.update(existing_matches)
    sorted_output = dict(sorted(disk_data.items(), key=lambda x: x[1].lower()))
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted_output, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved results to {OUTPUT_FILE}")
    filenames_to_remove = {os.path.splitext(os.path.basename(path))[0] for path in existing_matches.values()}
    if filenames_to_remove:
        remaining_filenames = sorted([fn for fn in initial_filenames if fn not in filenames_to_remove])
        with open(FILENAMES_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(remaining_filenames) + "\n")
        print(f"✅ Removed {len(filenames_to_remove)} found filenames from {FILENAMES_FILE}")


# --- MAIN (Using Process for workers) --- #
if __name__ == "__main__":
    q = Queue()
    matches_q = Queue()
    shutdown_flag = Event()

    print("--- Loading initial data... ---")
    folder_words = list(load_file_lines(FOLDER_FILE))
    initial_filenames = load_file_lines(FILENAMES_FILE)
    container_ids = load_file_lines(CONTAINERS_FILE)
    
    print(f"Folders: {len(folder_words)} | Filenames: {len(initial_filenames)} | Containers: {len(container_ids)}")

    approx_total = len(ROOTS) * (len(folder_words) ** MAX_DEPTH) * (len(initial_filenames) * len(EXTENSIONS))
    print(f"Estimated total candidates: ~{approx_total:,}\n")

    writer = Process(target=writer_reporter_process, args=(q, matches_q, shutdown_flag))
    writer.start()

    worker_args = [(root, folder_words, initial_filenames, EXTENSIONS, MAX_DEPTH, 
                    container_ids, q, matches_q) for root in ROOTS]

    workers = []
    for args in worker_args:
        worker = Process(target=worker_task, args=args) 
        workers.append(worker)
        worker.start()
        
    start_time = time.time()
    
    try:
        for worker in workers:
            worker.join()
            
        print("\n--- All roots processed. Shutting down IO... ---")
    
    except KeyboardInterrupt:
        print("\n--- Interruption detected! Shutting down gracefully... ---")
        for worker in workers:
            worker.terminate()
            
    finally:
        shutdown_flag.set()
        writer.join(timeout=30) 
        elapsed = time.time() - start_time
        print(f"\n✨ Session complete. Elapsed time: {timedelta(seconds=int(elapsed))}")