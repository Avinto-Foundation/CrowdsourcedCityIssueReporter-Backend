from rest_framework import serializers

from .models import Issue


class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = [
            'id',
            'category',
            'ward',
            'title',
            'description',
            'latitude',
            'longitude',
            
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'priority','updated_at']

    def validate_category(self, value):
        if not value.is_active:
            raise serializers.ValidationError(
                "This category is currently inactive."
            )
        return value