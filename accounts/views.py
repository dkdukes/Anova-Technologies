from rest_framework import generics, filters
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response

from .models import CustomUser
from .serializers import (
    AdminCustomerSerializer,
    RegisterSerializer,
    LoginSerializer,
    AdminCreateUserSerializer,
    AdminUserSerializer,
    AdminUserUpdateSerializer,
    AdminUserPasswordSerializer,
)
from .permissions import IsStaffOrAdmin, IsAdmin


# =====================================================
# PUBLIC AUTHENTICATION
# =====================================================

class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = []


class LoginAPIView(TokenObtainPairView):
    serializer_class = LoginSerializer
    permission_classes = []


# =====================================================
# CUSTOMER MANAGEMENT
# =====================================================

class AdminCustomerListAPIView(generics.ListAPIView):
    queryset = CustomUser.objects.all().order_by("-created_at")

    serializer_class = AdminCustomerSerializer

    permission_classes = [IsStaffOrAdmin]

    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    search_fields = [
        "username",
        "first_name",
        "last_name",
        "email",
        "phone",
    ]

    ordering_fields = [
        "username",
        "email",
        "created_at",
        "updated_at",
    ]

    ordering = [
        "-created_at",
    ]


class AdminCustomerDetailAPIView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()

    serializer_class = AdminCustomerSerializer

    permission_classes = [IsStaffOrAdmin]


# =====================================================
# CREATE STAFF / ADMIN ACCOUNT
# =====================================================

class AdminCreateUserAPIView(generics.CreateAPIView):
    """
    Allows an existing admin to create
    staff or admin accounts.
    """

    serializer_class = AdminCreateUserSerializer

    permission_classes = [IsAdmin]


# =====================================================
# STAFF / ADMIN MANAGEMENT
# =====================================================

class AdminUserListAPIView(generics.ListAPIView):
    """
    List all staff and admin accounts.

    Only administrators can access this endpoint.
    """

    serializer_class = AdminUserSerializer

    permission_classes = [IsAdmin]

    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    search_fields = [
        "username",
        "first_name",
        "last_name",
        "email",
        "phone",
    ]

    ordering_fields = [
        "username",
        "email",
        "created_at",
        "updated_at",
        "role",
        "is_active",
    ]

    ordering = [
        "-created_at",
    ]

    def get_queryset(self):
        return CustomUser.objects.filter(
            role__in=["staff", "admin"]
        ).order_by("-created_at")


class AdminUserDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):
    """
    View, edit, or delete a staff/admin account.

    Only administrators can access this endpoint.
    """

    permission_classes = [IsAdmin]

    def get_queryset(self):
        return CustomUser.objects.filter(
            role__in=["staff", "admin"]
        )

    def get_serializer_class(self):
        if self.request.method == "GET":
            return AdminUserSerializer

        return AdminUserUpdateSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = AdminUserSerializer(instance)

        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # ---------------------------------------------
        # Prevent admin from changing their own role
        # ---------------------------------------------

        if instance.id == request.user.id:

            if "role" in request.data:

                if request.data["role"] != request.user.role:
                    return Response(
                        {
                            "detail": (
                                "You cannot change your own role."
                            )
                        },
                        status=400,
                    )

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            AdminUserSerializer(
                serializer.instance
            ).data
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # ---------------------------------------------
        # Prevent admin from deleting themselves
        # ---------------------------------------------

        if instance.id == request.user.id:
            return Response(
                {
                    "detail": (
                        "You cannot delete your own account."
                    )
                },
                status=400,
            )

        # ---------------------------------------------
        # Prevent deleting the last active admin
        # ---------------------------------------------

        if instance.role == "admin":

            active_admin_count = CustomUser.objects.filter(
                role="admin",
                is_active=True,
            ).count()

            if active_admin_count <= 1:
                return Response(
                    {
                        "detail": (
                            "You cannot delete the last "
                            "active administrator."
                        )
                    },
                    status=400,
                )

        instance.delete()

        return Response(
            {
                "detail": (
                    "Account deleted successfully."
                )
            },
            status=204,
        )


# =====================================================
# ACTIVATE / RESTRICT ACCOUNT
# =====================================================

class AdminUserStatusAPIView(
    generics.UpdateAPIView
):
    """
    Activate or restrict a staff/admin account.
    """

    serializer_class = AdminUserSerializer

    permission_classes = [IsAdmin]

    def get_queryset(self):
        return CustomUser.objects.filter(
            role__in=["staff", "admin"]
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # ---------------------------------------------
        # Prevent admin from restricting themselves
        # ---------------------------------------------

        if instance.id == request.user.id:
            return Response(
                {
                    "detail": (
                        "You cannot restrict your own account."
                    )
                },
                status=400,
            )

        # ---------------------------------------------
        # Get requested status
        # ---------------------------------------------

        new_status = request.data.get(
            "is_active"
        )

        if new_status is None:
            return Response(
                {
                    "detail": (
                        "is_active is required."
                    )
                },
                status=400,
            )

        # ---------------------------------------------
        # Validate boolean value
        # ---------------------------------------------

        if isinstance(new_status, bool):
            pass

        elif isinstance(new_status, str):

            if new_status.lower() == "true":
                new_status = True

            elif new_status.lower() == "false":
                new_status = False

            else:
                return Response(
                    {
                        "detail": (
                            "is_active must be true or false."
                        )
                    },
                    status=400,
                )

        else:
            return Response(
                {
                    "detail": (
                        "is_active must be true or false."
                    )
                },
                status=400,
            )

        # ---------------------------------------------
        # Prevent restricting the last active admin
        # ---------------------------------------------

        if (
            instance.role == "admin"
            and instance.is_active
            and not new_status
        ):

            active_admin_count = CustomUser.objects.filter(
                role="admin",
                is_active=True,
            ).count()

            if active_admin_count <= 1:
                return Response(
                    {
                        "detail": (
                            "You cannot restrict the last "
                            "active administrator."
                        )
                    },
                    status=400,
                )

        # ---------------------------------------------
        # Save status
        # ---------------------------------------------

        instance.is_active = new_status

        instance.save(
            update_fields=[
                "is_active",
                "updated_at",
            ]
        )

        return Response(
            AdminUserSerializer(instance).data
        )


# =====================================================
# CHANGE PASSWORD
# =====================================================

class AdminUserPasswordAPIView(
    generics.UpdateAPIView
):
    """
    Allows an administrator to change another
    staff/admin user's password.
    """

    serializer_class = AdminUserPasswordSerializer

    permission_classes = [IsAdmin]

    def get_queryset(self):
        return CustomUser.objects.filter(
            role__in=["staff", "admin"]
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        instance.set_password(
            serializer.validated_data["password"]
        )

        instance.save(
            update_fields=["password"]
        )

        return Response(
            {
                "detail": (
                    "Password updated successfully."
                )
            }
        )