import os
import re
import subprocess

def preprocess_c_file(input_file: str, output_dir: str = "output") -> str:
    """Preprocesses the C file by merging user-defined includes, expanding macros, and removing all includes."""
    os.makedirs(output_dir, exist_ok=True)
    preprocessed_file = os.path.join(output_dir, "preprocessed.c")

    # Run GCC preprocessor
    cmd = [
        "gcc",
        "-nostdinc",       # Prevent standard system includes
        "-ffreestanding",  # Disable standard library assumptions
        "-E",              # Run preprocessor
        "-dD",             # Output macro definitions
        input_file,
        "-o", preprocessed_file,
        "-std=c99"
    ]

    try:
        subprocess.run(cmd, check=True, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Preprocessing failed:\nCommand: {e.cmd}\nError: {e.stderr.decode()}")

    return preprocessed_file