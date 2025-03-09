import os

def write_rust_file(segment_id: str, rust_code: str, metadata: dict, output_dir: str = "output"):
    """Writes translated Rust code and updates metadata.json with Rust file path."""
    rust_file_name = f"{segment_id}.rs"
    rust_file_path = os.path.join(output_dir, rust_file_name)

    os.makedirs(output_dir, exist_ok=True)
    with open(rust_file_path, "w") as f:
        f.write(rust_code)

    # Update metadata with Rust file path
    for segment in metadata["segments"]:
        if segment["segment_id"] == segment_id:
            segment["rust_file"] = rust_file_name
            break

    # Save updated metadata
    metadata_file = os.path.join(output_dir, "metadata.json")
    with open(metadata_file, "w") as f:
        json.dump(metadata, f, indent=4)

def combine_rust_segments(metadata_file: str, output_file: str):
    """Combines all Rust segments into one output.rs file based on metadata.json."""
    with open(metadata_file, "r") as f:
        metadata = json.load(f)

    combined_rust_code = ""
    for segment in metadata["segments"]:
        rust_file_name = segment.get("rust_file", "")
        rust_file_path = os.path.join(os.path.dirname(metadata_file), rust_file_name)

        if rust_file_name and os.path.exists(rust_file_path):
            with open(rust_file_path, "r") as f:
                combined_rust_code += f.read() + "\n\n"
        else:
            print(f"Warning: Rust file for segment {segment['segment_id']} not found: {rust_file_path}")

    with open(output_file, "w") as f:
        f.write(combined_rust_code)