from rest_framework import serializers
from .models import TrainingCourse, TrainingCategory
from core.models import User

class TrainingCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingCategory
        fields = ['id', 'name', 'style']

class TrainingCourseListSerializer(serializers.ModelSerializer):
    """Serializer for listing training courses"""
    category = TrainingCategorySerializer(read_only=True)
    created_by = serializers.SerializerMethodField()

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

    def get_created_by(self, obj):
        if obj.created_by:
            return {
                'id': obj.created_by.id,
                'email': obj.created_by.email
            }
        return None

class TrainingCourseCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating training courses"""
    category = serializers.CharField(write_only=True, required=False)
    created_by = serializers.CharField(write_only=True, required=False)

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
    
    def create(self, validated_data):
        category_name = validated_data.pop('category', None)
        created_by_email = validated_data.pop('created_by', None)
        
        # Handle category conversion
        if category_name:
            try:
                category = TrainingCategory.objects.get(name__iexact=category_name)
                validated_data['category'] = category
            except TrainingCategory.DoesNotExist:
                raise serializers.ValidationError({"category": f"Category '{category_name}' does not exist"})
        
        # Handle user conversion
        if created_by_email:
            try:
                user = User.objects.get(email=created_by_email)
                validated_data['created_by'] = user
            except User.DoesNotExist:
                raise serializers.ValidationError({"created_by": f"User with email '{created_by_email}' does not exist"})
        
        return super().create(validated_data) 

    def update(self, instance, validated_data):
        # Resolve and map category from a provided string name
        category_name = validated_data.pop('category', None)
        if category_name is not None:
            if category_name == "":
                validated_data['category'] = None
            else:
                try:
                    category = TrainingCategory.objects.get(name__iexact=category_name)
                    validated_data['category'] = category
                except TrainingCategory.DoesNotExist:
                    raise serializers.ValidationError({"category": f"Category '{category_name}' does not exist"})

        # Resolve and map created_by from a provided email
        created_by_email = validated_data.pop('created_by', None)
        if created_by_email is not None:
            if created_by_email == "":
                validated_data['created_by'] = None
            else:
                try:
                    user = User.objects.get(email=created_by_email)
                    validated_data['created_by'] = user
                except User.DoesNotExist:
                    raise serializers.ValidationError({"created_by": f"User with email '{created_by_email}' does not exist"})

        return super().update(instance, validated_data)