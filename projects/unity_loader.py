"""
Routes user questions to the right specialized agent.
"""

import os

# File types Unity projects use, grouped by which agent cares about them
UNITY_FILE_TYPES = {
    "codebase": [".cs", ".cginc", ".hlsl", ".shader", ".shadergraph", ".vfx"],
    "asset":    [".prefab", ".asset", ".mat", ".anim", ".controller", 
                ".physicMaterial", ".renderTexture", ".inputactions", ".lighting"],
    "world":    [".unity", ".json", ".txt"],
    "meta":     [".meta"]
}

# All supported extensions in one flat list for quick lookup
ALL_SUPPORTED = [ext for exts in UNITY_FILE_TYPES.values() for ext in exts]

def load_files_by_domain(root_path: str) -> dict:
    """
    Walk a Unity project folder and return files grouped by agent domain.
    """

    # Empty string bucket for domain
    grouped = {domain: "" for domain in UNITY_FILE_TYPES if domain != "meta"}

    for dirpath, _, filenames in os.walk(root_path):
        for filename in sorted(filenames):
            ext = os.path.splitext(filename)[1].lower()

            # Skip unsupported file types
            if ext not in ALL_SUPPORTED:
                continue

            # Skip .meta files
            if ext == ".meta":
                continue

            filepath = os.path.join(dirpath, filename)

            # Read the file as plain text
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except Exception as e:
                print(f"[UnityLoader] Could not read {filename}: {e}")
                continue

            # Figure out which domain this file belongs to
            domain = get_domain_for_extension(ext)
            if domain:
                grouped[domain] += f"\n\n// === {filename} ===\n{content}"

    return grouped

def load_all_as_string(root_path: str) -> str:
    """
    Load all supported Unity files and return them as one flat string.
    """

    grouped = load_files_by_domain(root_path)
    return "\n\n".join(grouped.values())


def get_domain_for_extension(ext: str) -> str:
    for domain, extensions in UNITY_FILE_TYPES.items():
        if ext in extensions and domain != "meta":
            return domain
    return None 

