import os
import json
import networkx as nx

def generate_metadata(symbols, segment_files, output_dir: str = "output"):
    """Generates metadata linking segments with extracted symbols."""
    os.makedirs(output_dir, exist_ok=True)
    metadata = {"segments": []}

    # Build dependency graph
    graph = nx.DiGraph()
    for symbol in symbols:
        graph.add_node(symbol["name"])
        for dependency in symbol["dependencies"]:
            graph.add_edge(symbol["name"], dependency)

    # Topological sorting (ensuring dependency order)
    try:
        sorted_symbols = list(nx.topological_sort(graph))
    except nx.NetworkXUnfeasible:
        raise ValueError("Dependency graph contains cycles!")

    for name in sorted_symbols:
        if name in segment_files:
            metadata["segments"].append({
                "segment_id": name,
                "file": segment_files[name],
                "rust_file": f"{name}.rs",
                "contained_symbols": [name],
                "dependencies": list(graph.successors(name))
            })

    metadata_file = os.path.join(output_dir, "metadata.json")
    with open(metadata_file, "w") as f:
        json.dump(metadata, f, indent=4)

    return metadata_file