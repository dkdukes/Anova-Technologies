
from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )

    class Meta:
        model = Review
        fields = [
            "id",
            "product",
            "username",
            "rating",
            "title",
            "comment",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "product",
            "username",
            "created_at",
            "updated_at",
        ]

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError(
                "Rating must be between 1 and 5."
            )
        return value

    def validate_comment(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                "Please enter a review comment."
            )
        return value.strip()
