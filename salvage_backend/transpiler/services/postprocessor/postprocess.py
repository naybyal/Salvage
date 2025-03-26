import os
import re
import json
from hashlib import md5
from collections import OrderedDict
from tree_sitter import Language, Parser
import tree_sitter_rust as tsrust

RUST_LANGUAGE = Language(tsrust.language())

def parse_rust_code(code: str):
    """Parse Rust code using tree-sitter and return the parse tree."""
    if RUST_LANGUAGE is None:
        raise RuntimeError("Rust language library not initialized")
    
    parser = Parser(RUST_LANGUAGE)
    return parser.parse(code.encode('utf8'))

def extract_function_signatures(code: str) -> list:
    """Extract function signatures using tree-sitter AST."""
    tree = parse_rust_code(code)
    root_node = tree.root_node
    signatures = []

    def traverse(node):
        if node.type == 'function_item':
            body_node = None
            for child in node.children:
                if child.type == 'block':
                    body_node = child
                    break
            if body_node:
                start = node.start_byte
                end = body_node.start_byte
                signature = code[start:end].strip()
            else:
                signature = code[node.start_byte:node.end_byte].strip()
            signatures.append(signature)
        for child in node.children:
            traverse(child)
    traverse(root_node)
    return signatures

def compute_segment_hash(segment: str) -> str:
    """Compute MD5 hash based on function signatures."""
    signatures = extract_function_signatures(segment)
    concatenated = ''.join(sorted(signatures))
    return md5(concatenated.encode('utf8')).hexdigest()

def remove_duplicate_segments(segments: dict) -> dict:
    """Remove segments with duplicate function signatures."""
    unique_segments = OrderedDict()
    seen_hashes = set()

    for name, code in segments.items():
        sig_hash = compute_segment_hash(code)
        if sig_hash not in seen_hashes:
            seen_hashes.add(sig_hash)
            unique_segments[name] = code
    return unique_segments

def extract_import_statements(segment: str) -> list:
    """Extract Rust imports using regex (handles multi-line)."""
    import_pattern = re.compile(r'^\s*use\b.*?;', re.MULTILINE | re.DOTALL)
    return import_pattern.findall(segment)

def deduplicate_imports(segments: list) -> tuple:
    """Deduplicate imports and remove them from segments."""
    all_imports = []
    cleaned_segments = []
    import_pattern = re.compile(r'^\s*use\b.*?;', re.MULTILINE | re.DOTALL)

    for seg in segments:
        imports = extract_import_statements(seg)
        all_imports.extend(imports)
        cleaned = import_pattern.sub('', seg).strip()
        cleaned_segments.append(cleaned)
    
    unique_imports = list(OrderedDict.fromkeys(all_imports))
    return unique_imports, cleaned_segments

def load_dependency_metadata(metadata_path: str) -> list:
    """Load sorted segment order from metadata."""
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    return metadata.get("sorted_segments", [])

def merge_segments(segments: dict, sorted_order: list, imports: list) -> str:
    """Merge segments with consolidated imports and in specified order."""
    merged_code = "// Merged Rust Code\n\n"
    if imports:
        merged_code += "// Imports\n" + "\n".join(imports) + "\n\n"
    for seg_name in sorted_order:
        if seg_name in segments:
            merged_code += f"// Segment: {seg_name}\n{segments[seg_name]}\n\n"
    return merged_code.strip()

def clean_and_merge_segments(segment_dir: str, metadata_path: str, output_path: str) -> str:
    # Load all segments
    segments = {}
    for filename in os.listdir(segment_dir):
        if filename.endswith('.rs'):
            with open(os.path.join(segment_dir, filename), 'r', encoding='utf8') as f:
                segments[filename] = f.read()

    # Remove duplicates
    unique_segments = remove_duplicate_segments(segments)
    segment_codes = list(unique_segments.values())

    # Deduplicate imports
    unique_imports, cleaned_segments = deduplicate_imports(segment_codes)

    # Rebuild cleaned mapping preserving order
    cleaned_mapping = OrderedDict()
    for (name, _), cleaned_code in zip(unique_segments.items(), cleaned_segments):
        cleaned_mapping[name] = cleaned_code

    # Determine merge order
    sorted_order = load_dependency_metadata(metadata_path)
    missing = [name for name in cleaned_mapping if name not in sorted_order]
    sorted_order += missing  # Append missing segments

    # Merge and save
    final_code = merge_segments(cleaned_mapping, sorted_order, unique_imports)
    with open(output_path, 'w', encoding='utf8') as f:
        f.write(final_code)
    return output_path

# Example usage:
# final_file = clean_and_merge_segments("segments_dir", "metadata.json", "output.rs")