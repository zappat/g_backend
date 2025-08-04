from django.urls import path
from .views import (
    TrainingCourseListCreateView,
    TrainingCourseDetailView,
    TrainingCategoryListCreateView,
    TrainingCategoryDetailView,
    TrainingCourseToggleVisibilityView
)

urlpatterns = [
    path('courses/', TrainingCourseListCreateView.as_view(), name='trainingcourse-list-create'),
    path('courses/<int:pk>/', TrainingCourseDetailView.as_view(), name='trainingcourse-detail'),
    path('courses/<int:pk>/toggle-visibility/', TrainingCourseToggleVisibilityView.as_view(), name='trainingcourse-toggle-visibility'),
    path('categories/', TrainingCategoryListCreateView.as_view(), name='trainingcategory-list-create'),
    path('categories/<int:pk>/', TrainingCategoryDetailView.as_view(), name='trainingcategory-detail'),
] 