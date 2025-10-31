import xxhash
import json

def generate_xxh64_hash(file_path: str) -> str:
    """Generate xxh64 hash for a given file path string and return it as a string."""
    file_path = file_path.lower().strip()  # Ensure lowercase, trim whitespace
    file_hash = int(xxhash.xxh64(file_path.encode('utf-8')).hexdigest(), 16)
    return file_hash

def process_file(input_filename: str, output_filename: str):
    """Read file paths from input file, generate hashes, and save as JSON."""
    results = {}
    
    with open(input_filename, "r", encoding="utf-8") as infile:
        for line in infile:
            file_path = line.strip()
            if file_path:
                hash_value = generate_xxh64_hash(file_path)
                results[hash_value] = file_path
    
    # Write results to JSON
    with open(output_filename, "w", encoding="utf-8") as outfile:
        json.dump(results, outfile, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    input_file = "DUMP.txt"
    output_file = "FilepathBruteOutput.json"
    
    process_file(input_file, output_file)
    print(f"Processed {input_file} → {output_file}")