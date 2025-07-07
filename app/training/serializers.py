from rest_framework import serializers
from .models import TrainingCourse, TrainingCategory

class TrainingCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingCategory
        fields = ['id', 'name']

class TrainingCourseSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=TrainingCategory.objects.all())
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = TrainingCourse
        fields = [
            'id',
            'title',
            'short_description',
            'category',
            'course_url',
            'thumbnail',
            'is_public',
            'created_at',
            'updated_at',
            'created_by',
        ] 