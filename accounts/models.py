from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    Permission
)
from django.utils import timezone
from .managers import UserManager


class Role(models.Model):
    """
    Dynamic Role Model
    """
    name = models.CharField(
        max_length=100, unique=True
        )
    description = models.TextField(
        blank=True
        )
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name="roles"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User Model
    """
    email = models.EmailField(unique=True)
    username = models.CharField(
        max_length=150,
        unique=True,
        blank=True,
        null=True
    )

    roles = models.ManyToManyField(
        Role,
        blank=True,
        related_name="users"
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    # -------- RBAC CORE --------
    def get_role_permissions(self):
        perms = set()
        for role in self.roles.filter(is_active=True):
            perms.update(
                role.permissions.values_list(
                    "content_type__app_label",
                    "codename"
                )
            )
        return perms

    def has_perm(self, perm, obj=None):
        if self.is_superuser:
            return True

        try:
            app_label, codename = perm.split(".")
        except ValueError:
            return False

        return (app_label, codename) in self.get_role_permissions()

    def has_module_perms(self, app_label):
        if self.is_superuser:
            return True

        return any(
            perm[0] == app_label for perm in self.get_role_permissions()
        )
