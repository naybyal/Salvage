from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from services.transpiler_workflow import run_transpilation_workflow
from celery.result import AsyncResult
import logging
import os

logger = logging.getLogger(__name__)

# Path to the shared output directory
SHARED_OUTPUT_PATH = '/shared_output/processed'

@api_view(['POST'])
def transpile_code(request):
    try:
        input_code = request.data.get('code')
        if not input_code:
            return Response({'error': 'No code provided'}, status=status.HTTP_400_BAD_REQUEST)

        from api.models import TranslationTask, File
        file_instance = File.objects.create(
            user=request.user,
            name="transpile",
            c_code=input_code,
            rust_code=""
        )
        translation_task = TranslationTask.objects.create(
            file=file_instance,
            status='in_progress'
        )
        
        # Pass file_instance.id to the workflow
        task_id = run_transpilation_workflow(input_code, file_id=file_instance.id)
        
        return Response({'task_id': task_id, 'status': 'processing'}, status=status.HTTP_202_ACCEPTED)
    
    except Exception as e:
        logger.error(f"Unexpected error in transpile_code: {str(e)}")
        return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
@api_view(['GET'])
def get_task_status(request):
    task_id = request.query_params.get('task_id')
    
    if not task_id:
        return Response(
            {'error': 'Task ID is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        result = AsyncResult(task_id)
        if result.ready():
            if result.successful():
                task_result = result.result
                # Try reading from the file first:
                final_rust_file_path = os.path.join(SHARED_OUTPUT_PATH, 'final_transpiled.rs')
                if os.path.exists(final_rust_file_path):
                    try:
                        with open(final_rust_file_path, 'r') as f:
                            rust_code = f.read()
                        # Remove markdown markers if present
                        if rust_code.startswith('```rust') and rust_code.endswith('```'):
                            rust_code = rust_code.strip('```rust').strip('```').strip()
                        return Response({
                            'status': 'completed',
                            'rust_code': rust_code,
                            'file_path': final_rust_file_path
                        })
                    except Exception as file_error:
                        logger.error(f"Error reading Rust file: {str(file_error)}")
                        return Response({
                            'status': 'error',
                            'error': f'Could not read Rust file: {str(file_error)}'
                        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    # File not available: try to fetch from the database
                    from api.models import TranslationResult, TranslationTask
                    # (Assuming you store the Celery task id or TranslationTask id somewhere accessible;
                    # you might need to modify your models to store this mapping.)
                    # For demonstration, assume you can get TranslationResult by filtering on a task ID that equals task_id.
                    try:
                        translation_result = TranslationResult.objects.get(task__celery_task_id=task_id)
                        return Response({
                            'status': 'completed',
                            'rust_code': translation_result.output,
                            'file_path': 'Database'
                        })
                    except TranslationResult.DoesNotExist:
                        return Response({
                            'status': 'error',
                            'error': 'Final result not found'
                        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                error = str(result.result) if result.result else "Unknown transpilation error"
                logger.error(f"Transpilation failed: {error}")
                return Response({
                    'status': 'failed',
                    'error': error
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Task is still processing
        return Response({
            'status': 'processing',
            'task_id': task_id
        }, status=status.HTTP_202_ACCEPTED)
    
    except Exception as e:
        logger.error(f"Error checking task status: {str(e)}")
        return Response({
            'status': 'error',
            'error': f'Error checking task status: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

urlpatterns = [
    path('transpile/', transpile_code, name='transpile'),
    path('transpile/status/', get_task_status, name='task_status'),
]