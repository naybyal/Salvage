import os
import re
import json
from hashlib import md5
from collections import OrderedDict
from tree_sitter import Language, Parser

# load the Rust language:
RUST_LANGUAGE = Language('build/my-languages.so', 'rust')

def parse_rust_code(code: str):
    """
    Parse Rust code using tree-sitter and return the parse tree.
    """
    parser = Parser()
    parser.set_language(RUST_LANGUAGE)
    tree = parser.parse(code.encode('utf8'))
    return tree

def extract_function_signatures(code: str) -> list:
    """
    Walk the AST and extract function signatures.
    For simplicity, we extract the text of each function item up to the opening brace '{'.
    """
    tree = parse_rust_code(code)
    root_node = tree.root_node
    signatures = []

    def traverse(node):
        # Tree-sitter node type for function items in Rust is usually 'function_item'
        if node.type == 'function_item':
            # Extract the text of the function item from the code
            # Find the first '{' if it exists
            text = code[node.start_byte:node.end_byte]
            brace_index = text.find('{')
            signature = text if brace_index == -1 else text[:brace_index].strip()
            if signature:
                signatures.append(signature)
        for child in node.children:
            traverse(child)

    traverse(root_node)
    return signatures

def compute_segment_hash(segment: str) -> str:
    """
    Compute a hash for a segment based on its extracted function signatures.
    This hash will help identify duplicate segments.
    """
    signatures = extract_function_signatures(segment)
    # Concatenate all signatures into one string
    concatenated = ''.join(sorted(signatures))
    return md5(concatenated.encode('utf8')).hexdigest()

def remove_duplicate_segments(segments: dict) -> dict:
    """
    Given a dictionary of segments {segment_name: code}, remove duplicates
    based on the computed signature hash. Returns a dictionary of unique segments.
    """
    unique_segments = {}
    seen_hashes = set()

    for name, code in segments.items():
        sig_hash = compute_segment_hash(code)
        if sig_hash not in seen_hashes:
            seen_hashes.add(sig_hash)
            unique_segments[name] = code
    return unique_segments

def extract_import_statements(segment: str) -> list:
    """
    Use regex to extract Rust import statements from a segment.
    Assumes that imports are written using the 'use' keyword.
    """
    import_pattern = re.compile(r'^\s*use\s+[^;]+;', re.MULTILINE)
    return import_pattern.findall(segment)

def deduplicate_imports(segments: list) -> tuple:
    """
    For a list of segments, extract and deduplicate all import statements.
    Returns a tuple: (unique_imports, segments_without_imports)
    """
    all_imports = []
    cleaned_segments = []
    for seg in segments:
        imports = extract_import_statements(seg)
        all_imports.extend(imports)
        # Remove import statements from the segment
        cleaned = re.sub(r'^\s*use\s+[^;]+;\s*', '', seg, flags=re.MULTILINE)
        cleaned_segments.append(cleaned.strip())
    unique_imports = list(OrderedDict.fromkeys(all_imports))
    return unique_imports, cleaned_segments

def load_dependency_metadata(metadata_path: str) -> dict:
    """
    Load dependency metadata from a JSON file.
    Expected format:
    {
        "sorted_segments": ["segmentA", "segmentB", ...]
    }
    """
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    return metadata.get("sorted_segments", [])

def merge_segments(segments: dict, sorted_order: list, imports: list) -> str:
    """
    Merge the ordered segments into a single Rust code string.
    """
    merged_code = ""
    # Consolidate imports at the top
    if imports:
        merged_code += "\n".join(imports) + "\n\n"
    for seg_name in sorted_order:
        if seg_name in segments:
            merged_code += f"// {seg_name}\n" + segments[seg_name] + "\n\n"
    return merged_code.strip()

def clean_and_merge_segments(segment_dir: str, metadata_path: str, output_path: str) -> str:
    """
    Orchestrates the cleaning and merging process:
      1. Load all .rs segment files from segment_dir.
      2. Remove duplicate segments.
      3. Deduplicate import statements across segments.
      4. Load dependency metadata (sorted order of segment names).
      5. Merge segments in that order with consolidated imports.
      6. Write the final merged code to output_path.
    Returns the path to the final output file.
    """
    # Load all segments into a dict: {filename: code}
    segments = {}
    for filename in os.listdir(segment_dir):
        if filename.endswith('.rs'):
            with open(os.path.join(segment_dir, filename), 'r', encoding='utf8') as f:
                segments[filename] = f.read()

    # Remove duplicate segments
    unique_segments = remove_duplicate_segments(segments)

    # Deduplicate imports
    segment_codes = list(unique_segments.values())
    unique_imports, cleaned_segments = deduplicate_imports(segment_codes)

    # Rebuild a mapping from segment name to cleaned code
    cleaned_mapping = {}
    for (name, _), cleaned_code in zip(unique_segments.items(), cleaned_segments):
        cleaned_mapping[name] = cleaned_code

    # Load dependency metadata for ordering (assumed to be a JSON file with a key "sorted_segments")
    sorted_order = load_dependency_metadata(metadata_path)
    # If metadata ordering doesn't include all segments, append the missing ones at the end
    for seg in cleaned_mapping.keys():
        if seg not in sorted_order:
            sorted_order.append(seg)

    # Merge segments according to sorted_order
    final_code = merge_segments(cleaned_mapping, sorted_order, unique_imports)

    # Write final merged code to output file
    with open(output_path, 'w', encoding='utf8') as f:
        f.write(final_code)

    return output_path

# Example usage (uncomment and adjust paths as needed):
# final_file = clean_and_merge_segments("path/to/segments", "path/to/metadata.json", "path/to/final_output.rs")
# print(f"Final transpiled Rust code saved to {final_file}")
