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
def create_transpile_chord(segmentation_result, file_id):
    """
    Create a transpile chord from segmentation results and include file_id
    so that the chord callback (postprocess_task) can update the File record.
    """
    # Attach file_id to segmentation_result if needed (for later reference)
    segmentation_result['file_id'] = file_id

    segment_files = segmentation_result['segments']
    sorted_segments = sorted(
        segment_files.items(),
        key=lambda item: int(re.search(r'segment_(\d+)_', item[0]).group(1))
                    if re.search(r'segment_(\d+)_', item[0]) else 0
    )

    transpile_tasks = [transpile_segment.s(path) for _, path in sorted_segments]

    # Pass file_id to the chord callback as a keyword argument.
    # This ensures that postprocess_task receives file_id along with the group result.
    chord_result = chord(transpile_tasks)(postprocess_task.s(file_id=file_id))
    
    return chord_result.id  # Return the chord callback task ID

def run_transpilation_workflow(input_file_path, file_id):
    workflow = chain(
        preprocess_task.s(input_file_path),
        extract_and_build_task.s(),
        segmentation_task.s(),
        # Using .s(file_id) here freezes the file_id as the second argument.
        create_transpile_chord.s(file_id)
    )
    result = workflow.apply_async()
    return result.id  # Return the task ID of the workflow's final task
