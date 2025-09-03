from django.urls import path
from .views import DocumentListCreateView, DocumentDetailView, DocumentDownloadView

urlpatterns = [
    path('documents/', DocumentListCreateView.as_view(), name='document-list-create'),
    path('documents/<int:pk>/', DocumentDetailView.as_view(), name='document-detail'),
    path('documents/<int:pk>/download/', DocumentDownloadView.as_view(), name='document-download'),
]