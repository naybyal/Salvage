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
        input_file = request.FILES.get('input_file')
        if not input_file:
            return Response(
                {"error": "No input file provided"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Save the uploaded file to a temporary location
        temp_file_path = default_storage.save(
            f'temp/{input_file.name}', ContentFile(input_file.read())
        )
        absolute_file_path = os.path.join(default_storage.location, temp_file_path)

        try:
            # Initiate the transpilation workflow
            result = run_transpilation_workflow(absolute_file_path)
            return Response(
                {"task_id": result.id, "status": "Workflow started"},
                status=status.HTTP_202_ACCEPTED
            )
        except Exception as e:
            logger.error(f"Transpilation error: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )