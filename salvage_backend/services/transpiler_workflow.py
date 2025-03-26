# salvage_backend/services/transpiler_workflow.py

from celery import chain, group, chord, Celery
from api.tasks import (
    preprocess_task,
    extract_and_build_task,
    segmentation_task,
    # create_transpile_chord,
    transpile_segment,
    postprocess_task,
)

app = Celery('salvage_backend')
@app.task
def create_transpile_chord(segmentation_result):
    segment_files = segmentation_result['segments']
    transpile_tasks = [transpile_segment.s(segment) for segment in segment_files]
    return chord(transpile_tasks)(postprocess_task.s())

def run_transpilation_workflow(input_file_path):
    """
    Orchestrates the full transpilation workflow as a Celery chain.
    """
    workflow = chain(
        preprocess_task.s(input_file_path),
        extract_and_build_task.s(),
        segmentation_task.s(),
        create_transpile_chord.s()
    )
    result = workflow.apply_async()
    return result