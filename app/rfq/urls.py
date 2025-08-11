from django.urls import path
from .views import RFQListCreateView, RFQDetailView, RFQAttachmentUploadView, RFQSaveView, RFQUpdateView

urlpatterns = [
    path('rfqs/', RFQListCreateView.as_view(), name='rfq-list-create'),
    path('rfqs/<int:pk>/', RFQDetailView.as_view(), name='rfq-detail'),
    path('rfqs/update/<int:pk>/', RFQUpdateView.as_view(), name='rfq-update'),
    path('rfqs/save/<int:rfq_id>/', RFQSaveView.as_view(), name='rfq-save'),
    path('rfqs/attachments/upload/', RFQAttachmentUploadView.as_view(), name='rfq-attachment-upload'),
] 