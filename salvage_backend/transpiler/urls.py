from django.urls import path
from .services.translator.translator import Transpiler
from rest_framework.decorators import api_view
from rest_framework.response import Response
from services.transpiler_workflow import run_transpilation_workflow
from celery.result import AsyncResult

@api_view(['POST'])
def transpile_code(request):
    input_code = request.data.get('code', '')
    # Start the Celery workflow
    result = run_transpilation_workflow(input_code)
    # Return the task ID to the client
    return Response({'task_id': result.id})

# def transpile_code(request):
#     c_code = request.data.get('code', '')
#     transpiler = Transpiler()
#     rust_code = transpiler.transpile(c_code)
#     return Response({'rust_code': rust_code})

@api_view(['GET'])
def get_task_status(request, task_id):
    result = AsyncResult(task_id)
    response_data = {
        'task_id': task_id,
        'status': result.status,
        'result': result.result if result.ready() else None
    }
    return Response(response_data)

urlpatterns = [
    path('transpile/', transpile_code, name='transpile'),
    # path('task-status/<str:task_id>/', get_task_status, name='task_status'),
]
