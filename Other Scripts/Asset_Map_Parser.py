import xml.etree.ElementTree as ET
import json

xml_file = "assets_map.xml"

# Ask the user for the filter type
FILTER_TYPE = input("Enter the Type to extract (e.g. Texture2D, Material): ").strip()

# Parse XML
tree = ET.parse(xml_file)
root = tree.getroot()

# Dictionary for Container -> Name
container_map = {}
found_strings = set()

for asset in root.findall("Asset"):
    name = asset.find("Name").text if asset.find("Name") is not None else None
    container = asset.find("Container").text if asset.find("Container") is not None else None
    type_elem = asset.find("Type").text if asset.find("Type") is not None else None

    if name and container and type_elem == FILTER_TYPE:
        container_map[container] = name
        found_strings.add(name)


sorted_files = sorted(found_strings)

# Output JSON file
json_file = f"assets_map_{FILTER_TYPE}.json"
path_file = f"assets_map_{FILTER_TYPE}.txt"
with open(json_file, "w", encoding="utf-8") as f:
    json.dump(container_map, f, indent=2, ensure_ascii=False)
with open(path_file, 'w', encoding='utf-8') as f:
    f.write("\n".join(sorted_files))

print(f"Saved {len(container_map)} entries of type '{FILTER_TYPE}' to {json_file}")
input("\nDone! Press Enter to close...")