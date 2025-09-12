from django.contrib import admin
from .models import TrainingCourse, TrainingCategory

@admin.register(TrainingCourse)
class TrainingCourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_public', 'created_at')
    search_fields = ('title', 'short_description')
    list_filter = ('is_public', 'category')

@admin.register(TrainingCategory)
class TrainingCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',) 