# api/tasks.py
from celery import shared_task
from .models import TranslationTask, TranslationResult, Analysis
import networkx as nx 

# from .utils.translation_pipeline import process_translation  # or from transpiler.translator import ...
# from .utils.performance import perform_analysis

@shared_task
def translation_task(task_id):
    """
    Perform code translation from C to Rust.
    """
    try:
        task = TranslationTask.objects.get(id=task_id)
        c_code = task.source_code.code
        # rust_code, logs = process_translation(c_code)

        # For demonstration, pretend the translator returns these:
        rust_code = "// Rust code"
        logs = "Translation logs..."

        # Save results
        TranslationResult.objects.update_or_create(
            translation_task=task,
            defaults={'rust_code': rust_code, 'compilation_logs': logs}
        )
        task.status = 'completed'
        task.save()
        return f"Translation {task_id} completed."
    except Exception as e:
        task.status = 'failed'
        task.save()
        return f"Translation {task_id} failed: {str(e)}"

@shared_task
def analysis_task(task_id, c_binary_path, rust_binary_path):
    """
    Compare performance of C and Rust binaries.
    """
    try:
        task = TranslationTask.objects.get(id=task_id)
        # results = perform_analysis(c_binary_path, rust_binary_path)
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


from celery import shared_task

@shared_task
def preprocess_task(input_file_path):
    from salvage_backend.transpiler.services.preprocessor.preprocess import preprocess_c_file  # import your function
    preprocessed_path = preprocess_c_file(input_file_path)
    return preprocessed_path

@shared_task
def extract_and_build_task(preprocessed_file):
    from salvage_backend.transpiler.services.preprocessor import extract_symbols, build_dependency_graph
    symbols = extract_symbols(preprocessed_file)
    graph = build_dependency_graph(symbols)
    return {"symbols": symbols, "graph_data": nx.readwrite.json_graph.node_link_data(graph)}


@shared_task
def segmentation_task(preprocessed_file, symbols):
    from salvage_backend.transpiler.services.preprocessor import segment_code, generate_metadata
    segments = segment_code(preprocessed_file, symbols)
    metadata_file = generate_metadata(symbols, segments)
    return {"segments": segments, "metadata": metadata_file}

@shared_task
def transpile_segment(segment_file):
    from salvage_backend.transpiler.services.translator import Transpiler
    with open(segment_file, "r") as f:
        c_code = f.read()
    transpiler = Transpiler()
    rust_code = transpiler.transpile(c_code)
    # Optionally, save the output to a file (e.g., segment name + ".rs")
    rust_file = segment_file.replace(".c", ".rs")
    with open(rust_file, "w") as f:
        f.write(rust_code)
    return rust_file

