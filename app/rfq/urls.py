from django.urls import path
from .views import RFQListCreateView, RFQDetailView, RFQAttachmentUploadView

urlpatterns = [
    path('rfqs/', RFQListCreateView.as_view(), name='rfq-list-create'),
    path('rfqs/<int:pk>/', RFQDetailView.as_view(), name='rfq-detail'),
    path('rfqs/attachments/upload/', RFQAttachmentUploadView.as_view(), name='rfq-attachment-upload'),
] 