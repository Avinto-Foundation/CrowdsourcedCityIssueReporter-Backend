
from rest_framework import serializers

from .models import Issue, IssueComment


class IssueSerializer(serializers.ModelSerializer):
    vote_count = serializers.IntegerField(
        source='votes.count',
        read_only=True
    )

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
            'vote_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'priority',
            'updated_at',
            'vote_count',
        ]

    def validate_category(self, value):
        if not value.is_active:
            raise serializers.ValidationError(
                "This category is currently inactive."
            )
        return value


class IssueCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = IssueComment
        fields = [
            'id',
            'issue',
            'user',
            'content',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'issue',
            'user',
            'created_at',
            'updated_at',
        ]
