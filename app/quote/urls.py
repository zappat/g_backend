from django.urls import path
from .views import QuoteListCreateView, QuoteDetailView, QuoteCountView, QuoteByRFQIdsView, QuoteAcceptView, QuoteRejectView


urlpatterns = [
    path('quotes/', QuoteListCreateView.as_view(), name='quote-list-create'),
    path('quotes/<int:pk>/', QuoteDetailView.as_view(), name='quote-detail'),
    path('quotes/count/<str:email>/', QuoteCountView.as_view(), name='quote-count'),
    path('quotes/get-by-rfq-ids/', QuoteByRFQIdsView.as_view(), name='quote-by-rfq-ids'),
    path('quotes/accept/<int:pk>/', QuoteAcceptView.as_view(), name='quote-accept'),
    path('quotes/reject/<int:pk>/', QuoteRejectView.as_view(), name='quote-reject'),
]

