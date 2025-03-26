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
        input_code = request.data.get('code')
        if not input_code:
            return Response(
                {"error": "No input code provided"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Save the input code to a temporary file
        temp_file_path = default_storage.save(
            f'temp/{request.FILES.get("input_file", "input")}.txt',  # You may adjust the file naming as needed
            ContentFile(input_code)
        )
        absolute_file_path = os.path.join(default_storage.location, temp_file_path)

        try:
            # Initiate the transpilation workflow
            result = run_transpilation_workflow(absolute_file_path)
            # Wait for the Celery workflow to complete (adjust the timeout as needed)
            final_output_path = result.get(timeout=300)  # e.g., wait up to 5 minutes
            if os.path.exists(final_output_path):
                with open(final_output_path, "r", encoding="utf-8") as f:
                    final_rust_code = f.read()
                return Response(
                    {"rust_code": final_rust_code},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"error": "Final output file not found."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except Exception as e:
            logger.error(f"Transpilation error: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )