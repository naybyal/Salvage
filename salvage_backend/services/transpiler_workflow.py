# salvage_backend/services/transpiler_workflow.py
import re
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
    """
    Given the segmentation result (a dict with a 'segments' key mapping segment names to file paths),
    sorts the segments in chronological (numerical) order and creates a chord of transpile_segment tasks.
    """
    segment_files = segmentation_result['segments']
    
    # Sort the segments by the numeric prefix in the key.
    # Assumes keys are in the format "segment_<number>_<name>.c"
    sorted_segments = sorted(
        segment_files.items(),
        key=lambda item: int(re.search(r'segment_(\d+)_', item[0]).group(1)) if re.search(r'segment_(\d+)_', item[0]) else 0
    )
    
    # For debugging/logging:
    for key, path in sorted_segments:
        print(f"Segment {key}: '{path}'")
    
    # Create a list of task signatures for each segment (using the sorted order)
    transpile_tasks = [transpile_segment.s(path) for _, path in sorted_segments]
    
    # Create a chord: all transpile tasks run in parallel, then postprocess_task is called on the results
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