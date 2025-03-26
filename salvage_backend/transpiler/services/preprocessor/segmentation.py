import os
import logging
from typing import List, Dict, Any
import clang.cindex
import networkx as nx

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def extract_symbols(file: str) -> List[Dict[str, Any]]:
    """
    Extracts function definitions, structs, unions, and optionally macros from a C file using Clang AST.
    Only symbols defined in the target file are extracted.
    
    :param file: The path to the preprocessed C file.
    :return: A list of dictionaries with symbol information.
    """
    index = clang.cindex.Index.create()
    try:
        translation_unit = index.parse(file)
    except clang.cindex.TranslationUnitLoadError as e:
        logging.error(f"Failed to parse {file}: {e}")
        return []
    
    symbols: List[Dict[str, Any]] = []

    def traverse(cursor: clang.cindex.Cursor) -> None:
        # Process only nodes that are defined in our file
        if cursor.location.file and os.path.abspath(cursor.location.file.name) != os.path.abspath(file):
            return

        if cursor.kind in (
            clang.cindex.CursorKind.FUNCTION_DECL,
            clang.cindex.CursorKind.STRUCT_DECL,
            clang.cindex.CursorKind.UNION_DECL,
            # clang.cindex.CursorKind.MACRO_DEFINITION,
        ):
            symbol = {
                "name": cursor.spelling,
                "kind": cursor.kind.name,
                "start_line": cursor.extent.start.line,
                "end_line": cursor.extent.end.line,
                "dependencies": []
            }
            # Extract dependencies: Filter for call expressions and declaration references
            for child in cursor.get_children():
                if child.kind in (clang.cindex.CursorKind.CALL_EXPR, clang.cindex.CursorKind.DECL_REF_EXPR):
                    dep = child.spelling
                    if dep and dep not in symbol["dependencies"]:
                        symbol["dependencies"].append(dep)
            
            logging.info(f"Extracted symbol: {symbol['name']} ({symbol['kind']}) from lines {symbol['start_line']}-{symbol['end_line']}")
            symbols.append(symbol)

        for child in cursor.get_children():
            traverse(child)

    traverse(translation_unit.cursor)
    return symbols

def build_dependency_graph(symbols: List[Dict[str, Any]]) -> nx.DiGraph:
    """
    Builds a dependency graph using function calls and struct references.
    
    :param symbols: List of symbol dictionaries.
    :return: A directed graph representing dependencies.
    """
    graph = nx.DiGraph()
    for symbol in symbols:
        graph.add_node(symbol["name"])
        for dependency in symbol["dependencies"]:
            graph.add_edge(symbol["name"], dependency)
    return graph

def segment_code(file: str, symbols: List[Dict[str, Any]], output_dir: str = "output") -> Dict[str, str]:
    """
    Segments code based on extracted symbols ensuring each segment's boundaries are within file limits.
    Writes each segment to a separate file and returns a mapping of symbol names to file paths.
    
    :param file: The path to the preprocessed C file.
    :param symbols: List of symbol dictionaries.
    :param output_dir: Directory where segments will be saved.
    :return: A dictionary mapping symbol names to segment file paths.
    """
    os.makedirs(output_dir, exist_ok=True)
    try:
        with open(file, "r") as f:
            lines = f.readlines()
    except IOError as e:
        logging.error(f"Error reading file {file}: {e}")
        return {}

    segments: Dict[str, str] = {}
    for symbol in symbols:
        start = symbol["start_line"] - 1  # Convert to 0-based index
        end = symbol["end_line"]
        if start < 0 or end > len(lines):
            logging.warning(f"Skipping symbol {symbol['name']} due to invalid line range: {start}-{end}")
            continue

        segment_text = "".join(lines[start:end])
        segments[symbol["name"]] = segment_text

    # Save segments to individual files
    segment_files: Dict[str, str] = {}
    for idx, (name, code) in enumerate(segments.items()):
        segment_file = os.path.join(output_dir, f"segment_{idx}_{name}.c")
        try:
            with open(segment_file, "w") as f:
                f.write(code)
            segment_files[name] = segment_file
            logging.info(f"Wrote segment for symbol {name} to {segment_file}")
        except IOError as e:
            logging.error(f"Failed to write segment for {name} to {segment_file}: {e}")

    return segment_files
