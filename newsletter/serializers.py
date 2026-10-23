
from rest_framework import serializers
from .models import NewsletterSubscriber


class NewsletterSubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterSubscriber
        fields = ["email"]

    def validate_email(self, value):
        email = value.strip().lower()

        if NewsletterSubscriber.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError(
                "This email is already subscribed."
            )

        return email
