"""
Parses individual game files into labeled chunks for ChromaDB indexing.
Splits large files into smaller semantic chunks for more precise retrieval.
"""

import os
import re
from projects.unity_loader import get_domain_for_extension

# Binary file types we can't read as text
BINARY_EXTENSIONS = {".fbx", ".png", ".jpg", ".jpeg", ".wav", ".mp3",
                     ".ogg", ".tga", ".exr", ".hdr"}

# How many lines before we split a non-code file into chunks
LINE_CHUNK_SIZE = 50


def parse_file(filepath: str) -> list[dict] | None:
    """
    Parse a single file and return a list of chunks.
    Returns None if the file should be skipped entirely.
    """

    filename = os.path.basename(filepath)
    ext = os.path.splitext(filename)[1].lower()

    # Handle double extensions like .fbx.meta
    is_meta = filename.endswith(".meta")
    base_ext = os.path.splitext(filename.replace(".meta", ""))[1].lower() if is_meta else ext

    # Skip .meta files for non-binary files — not useful
    if is_meta and base_ext not in BINARY_EXTENSIONS:
        return None

    # Binary files — just log their existence as one chunk
    if ext in BINARY_EXTENSIONS:
        return [_make_chunk(
            content=f"[Binary asset: {filename}]",
            filename=filename,
            filepath=filepath,
            extension=ext,
            domain="asset",
            chunk_index=0,
            is_binary=True
        )]

    # .fbx.meta and similar — read as text, one chunk
    if is_meta and base_ext in BINARY_EXTENSIONS:
        content = _read_text(filepath)
        if content is None:
            return None
        return [_make_chunk(
            content=content,
            filename=filename,
            filepath=filepath,
            extension=".meta",
            domain="asset",
            chunk_index=0,
            is_binary=False,
            describes_asset=base_ext
        )]

    # All other supported text files
    domain = get_domain_for_extension(ext)
    if domain is None:
        return None

    content = _read_text(filepath)
    if content is None:
        return None

    # C# files → chunk by method/class boundary
    if ext == ".cs":
        return _chunk_csharp(content, filename, filepath, domain)

    # Everything else → chunk by line count
    return _chunk_by_lines(content, filename, filepath, domain, ext)


def _chunk_csharp(content: str, filename: str, filepath: str, domain: str) -> list[dict]:
    """
    Split a C# file into chunks at class and method boundaries.
    Each public/private method or class becomes its own chunk.
    """

    chunks = []

    # Looks for lines starting with access modifiers or class declarations
    pattern = r'(?=\n\s*(?:public|private|protected|internal|static|override|virtual|abstract|class|interface|enum)\s)'
    sections = re.split(pattern, content)

    # Group sections into chunks 
    current_chunk = ""
    chunk_index = 0

    for section in sections:

        # If adding this section keeps us under 60 lines, combine it
        if len((current_chunk + section).splitlines()) <= 60:
            current_chunk += section
        else:

            # Save current chunk and start a new one
            if current_chunk.strip():
                chunks.append(_make_chunk(
                    content = current_chunk.strip(),
                    filename = filename,
                    filepath = filepath,
                    extension =".cs",
                    domain = domain,
                    chunk_index = chunk_index
                ))
                chunk_index += 1
            current_chunk = section

    # Don't forget the last chunk
    if current_chunk.strip():
        chunks.append(_make_chunk(
            content = current_chunk.strip(),
            filename = filename,
            filepath = filepath,
            extension = ".cs",
            domain = domain,
            chunk_index = chunk_index
        ))

    # If regex found nothing useful, fall back to the whole file as one chunk
    if not chunks:
        chunks.append(_make_chunk(
            content = content,
            filename = filename,
            filepath = filepath,
            extension = ".cs",
            domain = domain,
            chunk_index=0
        ))

    return chunks


def _chunk_by_lines(content: str, filename: str, filepath: str, domain: str, ext: str) -> list[dict]:
    """
    Split a file into chunks of LINE_CHUNK_SIZE lines each.
    Used for YAML-based Unity files like .unity, .prefab, .asset.
    """

    lines = content.splitlines()
    chunks = []

    # Slice the file into groups of LINE_CHUNK_SIZE lines
    for i in range(0, len(lines), LINE_CHUNK_SIZE):
        chunk_lines = lines[i:i + LINE_CHUNK_SIZE]
        chunk_content = "\n".join(chunk_lines)

        if chunk_content.strip():
            chunks.append(_make_chunk(
                content = chunk_content,
                filename = filename,
                filepath = filepath,
                extension = ext,
                domain = domain,
                chunk_index = i // LINE_CHUNK_SIZE
            ))

    return chunks


def _make_chunk(content: str, filename: str, filepath: str,
                extension: str, domain: str, chunk_index: int,
                is_binary: bool = False, describes_asset: str = None) -> dict:
    """
    Build a standardized chunk dict ready for ChromaDB.
    """

    metadata = {
        "filename": filename,
        "filepath": filepath,
        "extension": extension,
        "domain": domain,
        "chunk_index": chunk_index,
        "is_binary": is_binary
    }

    # Only add this field if it's a meta file describing a binary asset
    if describes_asset:
        metadata["describes_asset"] = describes_asset

    return {
        "content": content,
        "metadata": metadata
    }


def _read_text(filepath: str) -> str | None:
    """Read a file as plain text. Returns None if it fails."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        print(f"[Parser] Could not read {filepath}: {e}")
        return None
