from gettext import translation
from celery import shared_task, chord
import networkx as nx
import logging
from .models import TranslationTask, TranslationResult, Analysis
import os
import shutil
from django.db import transaction

logger = logging.getLogger(__name__)

SHARED_OUTPUT_DIR = "/shared_output/processed/"

# Task for performing code translation from C to Rust
@shared_task
def translation_task(task_id):
    """
    Perform code translation from C to Rust.
    """
    try:
        task = TranslationTask.objects.get(id=task_id)
        c_code = task.file.c_code  
        # Replace with actual translation logic when ready:
        rust_code = "// Rust code"
        logs = "Translation logs..."

        TranslationResult.objects.update_or_create(
            translation_task=task,
            defaults={'output': rust_code, 'created_at': task.created_at}
        )
        task.status = 'completed'
        task.save()
        return f"Translation {task_id} completed."
    except Exception as e:
        task.status = 'failed'
        task.save()
        return f"Translation {task_id} failed: {str(e)}"

# Task for analyzing performance comparing C and Rust binaries
@shared_task
def analysis_task(task_id, c_binary_path, rust_binary_path):
    """
    Compare performance of C and Rust binaries.
    """
    try:
        task = TranslationTask.objects.get(id=task_id)
        results = {
            "c_execution_time": 1.23,
            "rust_execution_time": 1.10,
            "c_memory_usage": 50.0,
            "rust_memory_usage": 45.0,
            "result_summary": "Rust is slightly faster"
        }
        Analysis.objects.update_or_create(
            translation_task=task,
            defaults={
                'c_execution_time': results["c_execution_time"],
                'rust_execution_time': results["rust_execution_time"],
                'c_memory_usage': results["c_memory_usage"],
                'rust_memory_usage': results["rust_memory_usage"],
                'result_summary': results["result_summary"],
            }
        )
        return f"Analysis for {task_id} completed."
    except Exception as e:
        return f"Analysis for {task_id} failed: {str(e)}"

# Task for preprocessing the C file
@shared_task
def preprocess_task(input_code):
    from transpiler.services.preprocessor.preprocess import preprocess_c_file 
    preprocessed_path = preprocess_c_file(input_code)
    return preprocessed_path

# Task for extracting symbols and building a dependency graph
@shared_task
def extract_and_build_task(preprocessed_file):
    from transpiler.services.preprocessor.segmentation import extract_symbols, build_dependency_graph
    symbols = extract_symbols(preprocessed_file)
    graph = build_dependency_graph(symbols)
    graph_data = nx.readwrite.json_graph.node_link_data(graph)
    # Return a dict containing both the preprocessed file path and the symbols
    return {"preprocessed_file": preprocessed_file, "symbols": symbols, "graph_data": graph_data}

# Updated segmentation task: accepts a single dictionary argument.
@shared_task
def segmentation_task(data):
    """
    Segments the preprocessed file using the extracted symbols.
    Expects a dict with keys 'preprocessed_file' and 'symbols'.
    """
    from transpiler.services.preprocessor.segmentation import segment_code
    from transpiler.services.preprocessor.metadata import generate_metadata
    preprocessed_file = data["preprocessed_file"]
    symbols = data["symbols"]
    segments = segment_code(preprocessed_file, symbols)
    metadata_file = generate_metadata(symbols, segments)
    return {"segments": segments, "metadata": metadata_file}

# Task for transpiling each segment individually
@shared_task
def transpile_segment(segment_file):
    from transpiler.services.translator.translator import Transpiler
    with open(segment_file, "r") as f:
        c_code = f.read()
    transpiler = Transpiler()
    rust_code = transpiler.transpile(c_code)
    rust_file = segment_file.replace(".c", ".rs")
    with open(rust_file, "w") as f:
        f.write(rust_code)
    return rust_file

# Task for postprocessing: cleaning and merging all Rust segments into one final file

@shared_task
def postprocess_task(result_from_chord, file_id=None):
    """
    Process the merged segments, write the final output file, and update
    the corresponding File record with the Rust code.
    """
    tmp_output = "/shared_output/processed/temp_final_output.rs"
    final_output = "/shared_output/processed/final_transpiled.rs"

    # Ensure directory exists
    os.makedirs(os.path.dirname(tmp_output), exist_ok=True, mode=0o755)

    # Call your merging function (this should write to tmp_output)
    from transpiler.services.postprocessor.postprocess import clean_and_merge_segments
    clean_and_merge_segments(
        segment_dir='/tmp/output/segments/',
        metadata_path='/tmp/output/metadata.json',
        output_path=tmp_output
    )

    # Atomically rename tmp_output to final_output
    os.rename(tmp_output, final_output)

    # Read the final content
    with open(final_output, "r", encoding="utf-8") as f:
        content = f.read()

    # If a file_id was passed, update the File record in the database.
    if file_id:
        try:
            from api.models import File
            from django.db import transaction
            with transaction.atomic():
                file_instance = File.objects.select_for_update().get(id=file_id)
                file_instance.rust_code = content
                file_instance.save()
        except Exception as db_error:
            # Log the error (you might want to raise or handle this further)
            import logging
            logger = logging.getLogger(__name__)
            logger.error("Error updating File (id=%s): %s", file_id, db_error)

    return {"path": final_output, "content": content}

@shared_task
def create_transpile_chord(segmentation_result):
    """
    Given segmentation result (a dict with a 'segments' key mapping symbol names to file paths),
    create a chord of transpile_segment tasks and trigger postprocess_task as callback.
    """
    segments = segmentation_result.get("segments", {})
    from api.tasks import transpile_segment, postprocess_task
    transpile_tasks = [transpile_segment.s(segment_file) for segment_file in segments.values()]
    return chord(transpile_tasks)(postprocess_task.s())

