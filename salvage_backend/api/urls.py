from django.urls import path
from .views import (
    SignupView,
    FileListCreateView,
    FileDetailView
)

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('files/', FileListCreateView.as_view(), name='file-list'),
    path('files/<int:pk>/', FileDetailView.as_view(), name='file-detail'),
]