import os
import subprocess
import tempfile
import logging
import re

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def preprocess_c_file(input_code: str) -> str:
    """
    Preprocesses the C code using GCC's preprocessor, removing includes and system headers.
    Expands macros and omits system includes using -nostdinc and -ffreestanding.
    
    Args:
        input_code (str): The C source code to preprocess.
    
    Returns:
        str: Path to the preprocessed file.
    """
    if not input_code:
        raise ValueError("Input code was not provided.")
    
    # Define problematic macros to neutralize them
    flags_to_ignore = [
        "-D__attribute__(x)=",
        "-D__filename=",
        "-D__modes=",
        "-D__stream=",
        "-D__buf=",
        "-D__has_feature(x)=0"
    ]
    
    # Create a temporary directory for output
    output_dir = tempfile.mkdtemp(prefix="preprocessed_")
    os.chmod(output_dir, 0o755)
    preprocessed_file = os.path.join(output_dir, "preprocessed.c")
    
    # Remove all #include directives from the input code
    processed_code = re.sub(
        r'^\s*#\s*include\s*[<"].*?[>"]\s*$', 
        '', 
        input_code, 
        flags=re.MULTILINE
    )
    
    # Write the processed code (without includes) to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".c") as temp_file:
        temp_file.write(processed_code.encode())
        temp_file_path = temp_file.name
    
    # Build the GCC preprocessor command with adjusted flags
    cmd = [
        "gcc",
        "-E",             # Preprocess only
        "-std=c99",
        "-nostdinc",      # Exclude system includes
        "-ffreestanding", # Assume no standard library
        "-dD"             # Output macro definitions
    ]
    cmd.extend(flags_to_ignore)
    cmd.extend([temp_file_path, "-o", preprocessed_file])
    
    logging.info("Running command: %s", " ".join(cmd))
    
    try:
        subprocess.run(
            cmd, 
            check=True, 
            stderr=subprocess.PIPE, 
            stdout=subprocess.PIPE, 
            text=True
        )
    except subprocess.CalledProcessError as e:
        error_output = e.stderr if e.stderr else "No error output."
        logging.error(
            f"Preprocessing failed:\nCommand: {' '.join(e.cmd)}\nError: {error_output}"
        )
        raise RuntimeError(f"Preprocessing failed: {error_output}") from e
    finally:
        os.remove(temp_file_path)
    
    if not os.path.isfile(preprocessed_file):
        raise RuntimeError("Preprocessing completed but the output file was not found.")
    
    return preprocessed_file