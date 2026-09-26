from rest_framework import serializers
from .models import CustomUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class AdminCustomerSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    order_count = serializers.SerializerMethodField()
    total_spent = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "phone",
            "profile_image",
            "role",
            "is_active",
            "is_staff",
            "order_count",
            "total_spent",
            "created_at",
            "updated_at",
        )

    def get_full_name(self, obj):
        full_name = f"{obj.first_name} {obj.last_name}".strip()
        return full_name or obj.username

    def get_order_count(self, obj):
        return obj.orders.count()

    def get_total_spent(self, obj):
        from django.db.models import Sum

        total = obj.orders.filter(
            payment_status="paid"
        ).aggregate(
            total=Sum("total")
        )["total"]

        return total or 0


class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    password2 = serializers.CharField(
        write_only=True
    )

    class Meta:
        model = CustomUser

        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "password",
            "password2",
        )

    def validate_username(self, value):
        value = value.strip()

        if CustomUser.objects.filter(
            username__iexact=value
        ).exists():
            raise serializers.ValidationError(
                "A user with this username already exists."
            )

        return value

    def validate_email(self, value):
        value = value.strip().lower()

        if CustomUser.objects.filter(
            email__iexact=value
        ).exists():
            raise serializers.ValidationError(
                "A user with this email already exists."
            )

        return value

    def validate(self, attrs):
        password = attrs.get("password")
        password2 = attrs.get("password2")

        if password != password2:
            raise serializers.ValidationError({
                "password2": "Passwords do not match."
            })

        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")

        password = validated_data.pop("password")

        user = CustomUser.objects.create_user(
            password=password,
            role="customer",
            **validated_data
        )

        return user


class LoginSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token["role"] = user.role
        token["username"] = user.username

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        data["user"] = {
            "id": self.user.id,
            "username": self.user.username,
            "email": self.user.email,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "phone": self.user.phone,
            "profile_image": self.user.profile_image,
            "role": self.user.role,
        }

        return data


class AdminCreateUserSerializer(serializers.ModelSerializer):
    """
    Serializer used by an existing admin to create
    staff or admin accounts.
    """

    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    role = serializers.ChoiceField(
        choices=[
            ("staff", "Staff"),
            ("admin", "Admin"),
        ]
    )

    class Meta:
        model = CustomUser

        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "password",
            "role",
        )

    def validate_username(self, value):
        value = value.strip()

        if CustomUser.objects.filter(
            username__iexact=value
        ).exists():
            raise serializers.ValidationError(
                "A user with this username already exists."
            )

        return value

    def validate_email(self, value):
        value = value.strip().lower()

        if CustomUser.objects.filter(
            email__iexact=value
        ).exists():
            raise serializers.ValidationError(
                "A user with this email already exists."
            )

        return value

    def create(self, validated_data):
        password = validated_data.pop("password")

        user = CustomUser.objects.create_user(
            password=password,
            **validated_data
        )

        return user



class AdminUserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "phone",
            "profile_image",
            "role",
            "is_active",
            "is_staff",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "full_name",
            "is_staff",
            "created_at",
            "updated_at",
        )

    def get_full_name(self, obj):
        full_name = f"{obj.first_name} {obj.last_name}".strip()

        return full_name or obj.username


class AdminUserUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser

        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "profile_image",
            "role",
        )

    def validate_username(self, value):
        value = value.strip()

        queryset = CustomUser.objects.filter(
            username__iexact=value
        ).exclude(
            pk=self.instance.pk
        )

        if queryset.exists():
            raise serializers.ValidationError(
                "A user with this username already exists."
            )

        return value

    def validate_email(self, value):
        value = value.strip().lower()

        queryset = CustomUser.objects.filter(
            email__iexact=value
        ).exclude(
            pk=self.instance.pk
        )

        if queryset.exists():
            raise serializers.ValidationError(
                "A user with this email already exists."
            )

        return value


class AdminUserPasswordSerializer(serializers.Serializer):

    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    password2 = serializers.CharField(
        write_only=True
    )

    def validate(self, attrs):

        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({
                "password2": "Passwords do not match."
            })

        return attrs