import xml.etree.ElementTree as ET

# Input XML file
xml_file = "assets_map.xml"

# Output TXT file
txt_file = "Containers.txt"

# Parse XML
tree = ET.parse(xml_file)
root = tree.getroot()

# Use a set to avoid duplicates
containers = set()

for asset in root.findall("Asset"):
    container = asset.find("Container").text if asset.find("Container") is not None else None
    if container:
        containers.add(container)

# Sort for consistency
unique_containers = sorted(containers)

# Write to text file (one per line)
with open(txt_file, "w", encoding="utf-8") as f:
    f.write("\n".join(unique_containers))

print(f"Saved {len(unique_containers)} unique container IDs to {txt_file}")
input("\nDone! Press Enter to close...")