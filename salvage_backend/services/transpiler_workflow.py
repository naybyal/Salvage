# salvage_backend/services/transpiler_workflow.py

from celery import chain, group
from api.tasks import (
    preprocess_task,
    extract_and_build_task,
    segmentation_task,
    transpile_segment,
    postprocess_task,
)

def run_transpilation_workflow(input_file, segment_files):
    """
    Orchestrates the full transpilation workflow as a Celery chain.
    
    Parameters:
      - input_file: Path to the input C file.
      - segment_files: List of segment identifiers or file paths produced by segmentation.
        (This should match the output of your segmentation_task.)
    
    Returns:
      A Celery AsyncResult object.
    """
    workflow = chain(
        preprocess_task.s(input_file),
        extract_and_build_task.s(),
        segmentation_task.s(),
        # Here we assume segmentation_task returns a list of segment file paths.
        group(transpile_segment.s(segment_file) for segment_file in segment_files),
        postprocess_task.s()
    )
    return workflow.delay()
