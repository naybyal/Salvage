import os
import logging
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import get_user_model
from .models import File
from .serializers import UserSerializer, FileSerializer
from services.transpiler_workflow import run_transpilation_workflow
from celery.result import AsyncResult
from django.conf import settings

logger = logging.getLogger(__name__)
User = get_user_model()

class SignupView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(
                    {"message": "User created successfully"},
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                logger.error(f"Registration error: {str(e)}")
                return Response(
                    {"error": "Registration failed"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FileListCreateView(generics.ListCreateAPIView):
    serializer_class = FileSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return File.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class FileDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FileSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return File.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        instance.delete()

class TranspileAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            # Start workflow and return task ID
            task_id = run_transpilation_workflow(request.data['code'])
            return Response(
                {"task_id": task_id, "status": "processing"},
                status=status.HTTP_202_ACCEPTED
            )
        except KeyError as e:
            logger.error(f"Missing data: {str(e)}")
            return Response(
                {"error": "Invalid request format"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected error in transpilation: {str(e)}")
            return Response(
                {"error": f"Transpilation error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get(self, request):
        task_id = request.query_params.get("task_id")
        if not task_id:
            return Response({"error": "Task ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        result = AsyncResult(task_id, app=settings.CELERY_APP)
        logger.info(f"Task {task_id} status: {result.state}, result: {result.result}")

        if result.ready():
            if result.successful():
                try:
                    # More robust error checking and result extraction
                    task_result = result.result
                    
                    # Check if result is a dictionary with 'content' and 'path'
                    if isinstance(task_result, dict):
                        rust_code = task_result.get('content')
                        file_path = task_result.get('path')
                        
                        if rust_code and file_path:
                            # Extract Rust code from markdown-like code block if necessary
                            if rust_code.startswith('```rust') and rust_code.endswith('```'):
                                rust_code = rust_code.strip('```rust').strip('```').strip()
                            
                            return Response({
                                "rust_code": rust_code, 
                                "file_path": file_path
                            })
                    
                    # If the above checks fail, try to get Rust code directly
                    if isinstance(task_result, str) and task_result.strip():
                        # Extract Rust code from markdown-like code block if necessary
                        if task_result.startswith('```rust') and task_result.endswith('```'):
                            task_result = task_result.strip('```rust').strip('```').strip()
                        
                        return Response({"rust_code": task_result})
                    
                    # If no valid result found
                    logger.error(f"Unexpected task result format: {task_result}")
                    return Response(
                        {"error": "Unexpected result format"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                
                except Exception as e:
                    logger.error(f"Error processing task result: {str(e)}")
                    return Response(
                        {"error": f"Error processing result: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            else:
                # Task failed
                error = result.result if result.result else "Unknown transpilation error"
                logger.error(f"Transpilation failed: {error}")
                return Response(
                    {"error": "Transpilation failed", "details": str(error)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        # Task is still processing
        return Response({"status": "processing"}, status=status.HTTP_202_ACCEPTED)