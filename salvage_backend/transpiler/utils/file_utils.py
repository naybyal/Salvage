import os
import json
import logging

logger = logging.getLogger(__name__)


def write_rust_file(segment_id: str, rust_code: str, metadata: dict, output_dir: str):
    """Writes translated Rust code and updates metadata.json with Rust file path."""
    try:
        rust_file_name = f"{segment_id}.rs"
        rust_file_path = os.path.join(output_dir, rust_file_name)

        # Create directory if not exists
        os.makedirs(output_dir, exist_ok=True)

        # Write Rust code
        with open(rust_file_path, "w") as f:
            f.write(rust_code)

        # Update metadata
        for segment in metadata["segments"]:
            if segment["segment_id"] == segment_id:
                segment["rust_file"] = rust_file_name
                break

        # Save updated metadata
        metadata_file = os.path.join(output_dir, "metadata.json")
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=4)

    except Exception as e:
        logger.error(f"Failed to write Rust file for segment {segment_id}: {str(e)}")
        raise


def combine_rust_segments(metadata_file: str, output_file: str):
    """Combines all Rust segments into one output file."""
    try:
        with open(metadata_file, "r") as f:
            metadata = json.load(f)

        combined_rust_code = []
        metadata_dir = os.path.dirname(metadata_file)

        for segment in metadata["segments"]:
            rust_file_name = segment.get("rust_file")
            if not rust_file_name:
                logger.warning(f"Missing rust_file for segment {segment['segment_id']}")
                continue

            rust_file_path = os.path.join(metadata_dir, rust_file_name)

            if not os.path.exists(rust_file_path):
                logger.error(f"Rust file not found: {rust_file_path}")
                continue

            with open(rust_file_path, "r") as f:
                combined_rust_code.append(f.read())

        # Write combined output with proper spacing
        with open(output_file, "w") as f:
            f.write("\n\n".join(combined_rust_code))

    except Exception as e:
        logger.error(f"Failed to combine Rust segments: {str(e)}")
        raise