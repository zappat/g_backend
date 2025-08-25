from django.urls import path
from .views import QuoteListCreateView, QuoteDetailView, QuoteCountView


urlpatterns = [
    path('quotes/', QuoteListCreateView.as_view(), name='quote-list-create'),
    path('quotes/<int:pk>/', QuoteDetailView.as_view(), name='quote-detail'),
    path('quotes/count/<str:email>/', QuoteCountView.as_view(), name='quote-count'),
]

