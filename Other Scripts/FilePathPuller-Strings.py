import re
from pathlib import Path

def extract_filepaths(base_folder, output_file):

    EXTENSIONS = [
        # IMAGES
        ".png", ".tga", ".jpg", ".jpeg", ".dds", ".psd",
        # MATERIALS
        ".mat", ".physicMaterial", ".compute", ".cube", ".shader",
        # ANIMATIONS / MODELS
        ".fbx", ".obj", ".anim", ".mesh",
        # UNITY FILES
        ".unity", ".prefab", ".asset",
        # SPINE FILES
        ".atlas", ".skel", ".spine",
        # DATA FILES
        ".bytes", ".json", ".txt", ".dat", ".cs", ".otf", ".srt", ".csv", ".html",
        # AUDIO / VIDEO
        ".pck", ".bnk", ".mp4", ".usm", ".mov",
        # OTHER
        ".CustomPropertyUI", ".patch", ".playable", ".diff", ".log",
    ]

    # Build regex dynamically from EXTENSIONS
    ext_pattern = "|".join(re.escape(ext.lstrip(".")) for ext in EXTENSIONS)
    filepath_pattern = re.compile(
        rf'(?:Assets|UI|IconRole|OriginalResRepos|ART|Data|Scenes)/[^",\s]+\.(?:{ext_pattern})',
        re.IGNORECASE
    )

    remove_ext_pattern = re.compile(rf'\.(?:{ext_pattern})$', re.IGNORECASE)

    # Load existing data
    output_path = Path(output_file)
    existing_strings = set()
    if output_path.exists():
        with output_path.open('r', encoding='utf-8', errors='ignore') as f:
            existing_strings = {line.strip() for line in f if line.strip()}

    found_strings = set(existing_strings)

    base_path = Path(base_folder)
    for path in base_path.rglob("*"):
        if path.is_dir():
            continue

        try:
            text = path.read_text(encoding='utf-8')
            for result in filepath_pattern.finditer(text):
                for sub_match in result.group(0).split(','):
                    sub_match = sub_match.strip()
                    if not sub_match:
                        continue

                    # Apply prefix rules
                    if sub_match.startswith("UI/"):
                        sub_match = f"Assets/NapResources/{sub_match}"
                    elif sub_match.startswith("IconRole"):
                        sub_match = f"Assets/NapResources/UI/Sprite/A1DynamicLoad/{sub_match}"
                    elif sub_match.startswith("Data"):
                        sub_match = f"Assets/NapResources/{sub_match}"

                    # Remove extension dynamically
                    sub_match = remove_ext_pattern.sub('', sub_match)

                    found_strings.add(sub_match)

        except Exception as e:
            print(f"Error processing {path}: {e}")

    new_entries = found_strings - existing_strings
    sorted_file_paths = sorted(found_strings)

    if new_entries:
        with output_path.open('w', encoding='utf-8') as f:
            f.write("\n".join(sorted_file_paths))
        print(f"✅ Added {len(new_entries)} new strings. Total now: {len(found_strings)}.")
    else:
        print("✅ No new strings found. Everything is up to date.")

# Example usage
base_folder = r"F:\ZenlessData"
output_file = "extracted_filepaths.txt"
extract_filepaths(base_folder, output_file)
