from django.urls import path
from .views import QuoteListCreateView, QuoteDetailView, QuoteCountView, QuoteByRFQIdsView


urlpatterns = [
    path('quotes/', QuoteListCreateView.as_view(), name='quote-list-create'),
    path('quotes/<int:pk>/', QuoteDetailView.as_view(), name='quote-detail'),
    path('quotes/count/<str:email>/', QuoteCountView.as_view(), name='quote-count'),
    path('quotes/get-by-rfq-ids/', QuoteByRFQIdsView.as_view(), name='quote-by-rfq-ids'),
]

