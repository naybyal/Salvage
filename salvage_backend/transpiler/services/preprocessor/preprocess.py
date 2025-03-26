import os
import subprocess
import tempfile
import sys

def find_standard_include_paths():
    """
    Dynamically find standard include paths for the current system.
    
    Returns:
    list: A list of standard include paths for C headers
    """
    include_paths = []
    
    # Common include path locations
    potential_paths = [
        # GCC include paths
        '/usr/lib/gcc',
        '/usr/local/include',
        '/usr/include',
        
        # Clang include paths
        '/usr/lib/llvm',
        '/usr/include/clang',
        
        # System-specific paths
        '/usr/include/x86_64-linux-gnu',
    ]
    
    # Try to find existing gcc/clang include paths
    for base_path in potential_paths:
        if os.path.exists(base_path):
            # Walk through potential GCC/Clang versions
            for root, dirs, _ in os.walk(base_path):
                for dir_name in dirs:
                    full_path = os.path.join(root, dir_name)
                    # More robust header checking
                    try:
                        if 'include' in full_path and os.path.isfile(os.path.join(full_path, 'stddef.h')):
                            include_paths.append(full_path)
                    except Exception:
                        pass
    
    # Fallback to using gcc to find include paths
    try:
        # Use gcc instead of gcc -v to get more reliable results
        gcc_paths = subprocess.check_output(['gcc', '-xc', '-E', '-v', '/dev/null'], 
                                            stderr=subprocess.STDOUT, 
                                            universal_newlines=True)
        
        # More precise parsing of include paths
        include_search_paths = [
            line.strip() for line in gcc_paths.split('\n') 
            if line.strip().startswith('/') and ('include' in line or 'gcc' in line)
        ]
        include_paths.extend(include_search_paths)
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # More aggressive deduplication and filtering
    include_paths = list(set(
        path for path in include_paths 
        if os.path.exists(path) and os.path.isdir(path)
    ))
    
    # Optional: Print out the detected include paths for debugging
    print("Detected Include Paths:", include_paths)
    
    return include_paths

def preprocess_c_file(input_code: str) -> str:
    """
    Preprocesses the C code using a more robust method.
    
    Args:
        input_code (str): The C source code to preprocess.
    
    Returns:
        str: Path to the preprocessed file.
    """
    if not input_code:
        raise ValueError("Input code was not provided.")
    
    # Dynamically find include paths
    include_paths = find_standard_include_paths()
    
    if not include_paths:
        raise RuntimeError("Could not find any standard include paths.")
    
    # Prepare include flags
    include_flags = [f"-I{path}" for path in include_paths]
    
    # Create a temporary directory for output
    output_dir = tempfile.mkdtemp(prefix="preprocessed_")
    os.chmod(output_dir, 0o755)
    preprocessed_file = os.path.join(output_dir, "preprocessed.c")
    
    # Create a temporary file for the input C code
    with tempfile.NamedTemporaryFile(delete=False, suffix=".c") as temp_file:
        temp_file.write(input_code.encode())
        temp_file_path = temp_file.name
    
    # Build the preprocessor command
    cmd = [
        "gcc",
        "-E",  # Preprocess only
        "-dD",  # Output macro definitions
        "-std=c99"
    ]
    
    # Add include paths
    cmd.extend(include_flags)
    
    # Add input and output files
    cmd.extend([temp_file_path, "-o", preprocessed_file])
    
    try:
        # Run the preprocessor
        result = subprocess.run(
            cmd, 
            check=True, 
            stderr=subprocess.PIPE, 
            stdout=subprocess.PIPE, 
            text=True
        )
    except subprocess.CalledProcessError as e:
        # Detailed error logging
        error_output = e.stderr or "No error output."
        raise RuntimeError(f"""
Preprocessing failed:
Command: {' '.join(cmd)}
Error: {error_output}
Include Paths: {include_paths}
""") from e
    finally:
        # Clean up the temporary input file
        os.remove(temp_file_path)
    
    if not os.path.isfile(preprocessed_file):
        raise RuntimeError("Preprocessing completed but the output file was not found.")
    
    return preprocessed_file