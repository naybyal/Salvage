import os
import clang.cindex
import networkx as nx

def extract_symbols(file: str):
    """Extracts function definitions, structs, and macros using Clang AST."""
    index = clang.cindex.Index.create()
    translation_unit = index.parse(file)
    symbols = []

    def traverse(cursor):
        if cursor.kind in (
            clang.cindex.CursorKind.FUNCTION_DECL,
            clang.cindex.CursorKind.STRUCT_DECL,
            clang.cindex.CursorKind.UNION_DECL,
            clang.cindex.CursorKind.MACRO_DEFINITION,
        ):
            symbol = {
                "name": cursor.spelling,
                "kind": cursor.kind.name,
                "start_line": cursor.extent.start.line,
                "end_line": cursor.extent.end.line,
                "dependencies": [],
            }
            # Extract dependencies (function calls, struct usage)
            for child in cursor.get_children():
                if child.kind.is_reference():
                    symbol["dependencies"].append(child.spelling)

            symbols.append(symbol)

        for child in cursor.get_children():
            traverse(child)

    traverse(translation_unit.cursor)
    return symbols

def build_dependency_graph(symbols):
    """Builds a dependency graph using function calls and struct references."""
    graph = nx.DiGraph()
    for symbol in symbols:
        graph.add_node(symbol["name"])
        for dependency in symbol["dependencies"]:
            graph.add_edge(symbol["name"], dependency)
    return graph

def segment_code(file: str, symbols, output_dir: str = "output"):
    """Segments code based on extracted symbols and ensures coherent segments."""
    os.makedirs(output_dir, exist_ok=True)
    with open(file, "r") as f:
        lines = f.readlines()

    segments = {}
    for symbol in symbols:
        start, end = symbol["start_line"] - 1, symbol["end_line"]
        if start < 0 or end > len(lines):
            continue

        segment_code = "".join(lines[start:end])
        segments[symbol["name"]] = segment_code

    # Save segments to files
    segment_files = {}
    for idx, (name, code) in enumerate(segments.items()):
        segment_file = os.path.join(output_dir, f"segment_{idx}.c")
        with open(segment_file, "w") as f:
            f.write(code)
        segment_files[name] = segment_file

    return segment_files