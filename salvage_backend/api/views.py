from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .models import File
from .serializers import UserSerializer, FileSerializer
import logging
from rest_framework_simplejwt.authentication import JWTAuthentication
from salvage_backend.services.transpiler_workflow import run_transpilation_workflow


logger = logging.getLogger(__name__)
User = get_user_model()

class SignupView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
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
        # Remove the file limit check
        serializer.save(user=self.request.user)

class FileDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FileSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return File.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class TranspileAPIView(APIView):
    def post(self, request):
        input_file = request.data.get("input_file")
        # Optionally, process and store the file, then pass its path
        segment_files = []  # You'd derive this from your segmentation logic.
        result = run_transpilation_workflow(input_file, segment_files)
        return Response({"task_id": result.id, "status": "Workflow started"})