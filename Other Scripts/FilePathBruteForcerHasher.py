import xxhash

containers_file = "Containers.txt"

# --- Load container IDs ---
with open(containers_file, "r", encoding="utf-8") as f:
    container_ids = {int(line.strip()) for line in f if line.strip()}

def generate_xxh64_hash(file_path: str):
    """Generate xxh64 hash for a given file path string."""
    file_path = file_path.lower()
    file_hash = int(xxhash.xxh64(file_path.encode('utf-8')).hexdigest(), 16)

    if file_hash in container_ids:
        print(f'[MATCH]: "{file_hash}": "{input_path}",')
    else:
        print(f'[NO MATCH]: "{file_hash}": "{input_path}",')

# Loop to allow multiple inputs
while True:
    input_path = input("Enter file path (or type 'exit' to quit): ").strip()
    
    if input_path.lower() == 'exit':
        print("Exiting...")
        break
    
    if input_path:
        generate_xxh64_hash(input_path)
    else:
        print("Please enter a valid file path.")