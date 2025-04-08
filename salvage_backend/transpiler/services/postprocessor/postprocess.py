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
            # Capture the function signature (everything until the body)
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

def strip_rust_code_fences(code: str) -> str:
    """Remove Markdown code fences like ```rust ... ``` or ``` ... ``` from code."""
    code = code.strip()
    code = re.sub(r'^```(?:rust)?\s*', '', code)
    code = re.sub(r'\s*```$', '', code)
    return code.strip()

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

def deduplicate_functions_in_merged_code(code: str) -> str:
    """
    Remove duplicate Rust function definitions by comparing name and signature.
    Retain the most complete version (based on function body length).
    """
    tree = parse_rust_code(code)
    func_nodes = []

    def traverse(node):
        if node.type == 'function_item':
            func_nodes.append(node)
        for child in node.children:
            traverse(child)
    traverse(tree.root_node)

    seen = {}
    for node in func_nodes:
        func_code = code[node.start_byte:node.end_byte]
        name = None
        for child in node.children:
            if child.type == 'identifier':
                name = code[child.start_byte:child.end_byte]
                break
        if name:
            existing = seen.get(name)
            if existing is None or len(func_code.strip()) > len(existing['code'].strip()):
                seen[name] = {'code': func_code, 'start': node.start_byte, 'end': node.end_byte}

    # Remove all duplicates
    new_code = code
    removal_ranges = []
    for node in func_nodes:
        name = None
        for child in node.children:
            if child.type == 'identifier':
                name = code[child.start_byte:child.end_byte]
                break
        if name and (code[node.start_byte:node.end_byte] != seen[name]['code']):
            removal_ranges.append((node.start_byte, node.end_byte))

    for start, end in sorted(removal_ranges, reverse=True):
        new_code = new_code[:start] + new_code[end:]

    return new_code



def load_dependency_metadata(metadata_path: str) -> list:
    """Load sorted segment order from metadata."""
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    return metadata.get("sorted_segments", [])

def merge_segments(segments: dict, sorted_order: list, imports: list) -> str:
    """Merge segments with consolidated imports and in specified order."""
    merged_code = ""
    if imports:
        merged_code += "// Imports\n" + "\n".join(imports) + "\n\n"
    for seg_name in sorted_order:
        if seg_name in segments:
            merged_code += f"// Segment: {seg_name}\n{segments[seg_name]}\n\n"
    return merged_code.strip()


def cleanup_segments(segment_dir: str):
    """
    Delete all files in the given segment directory.
    If the directory is no longer needed, it can be removed entirely.
    """
    if os.path.exists(segment_dir):
        for filename in os.listdir(segment_dir):
            file_path = os.path.join(segment_dir, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"Deleted file: {file_path}")
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")

def clean_and_merge_segments(segment_dir: str, metadata_path: str, output_path: str) -> str:
    if not os.path.exists(segment_dir):
        raise ValueError(f"Segment directory {segment_dir} does not exist!")
    
    segments = {}
    for filename in os.listdir(segment_dir):
        if filename.endswith('.rs'):
            with open(os.path.join(segment_dir, filename), 'r', encoding='utf8') as f:
                raw_code = f.read()
                cleaned_code = strip_rust_code_fences(raw_code)
                segments[filename] = cleaned_code

    # Remove duplicate segments (based on function signatures)
    unique_segments = remove_duplicate_segments(segments)
    segment_codes = list(unique_segments.values())

    # Deduplicate import statements from the segments
    unique_imports, cleaned_segments = deduplicate_imports(segment_codes)

    # Rebuild mapping preserving order
    cleaned_mapping = OrderedDict()
    for (name, _), cleaned_code in zip(unique_segments.items(), cleaned_segments):
        cleaned_mapping[name] = cleaned_code

    # Determine merge order from metadata
    sorted_order = load_dependency_metadata(metadata_path)
    missing = [name for name in cleaned_mapping if name not in sorted_order]
    sorted_order += missing  # Append any missing segments

    # Merge segments and imports into a single code string
    final_rust_code = merge_segments(cleaned_mapping, sorted_order, unique_imports)

    # Run function deduplication on the merged code
    final_rust_code = deduplicate_functions_in_merged_code(final_rust_code)

    # Save final code to the output file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_rust_code)

    cleanup_segments(segment_dir)
        
    return output_path
