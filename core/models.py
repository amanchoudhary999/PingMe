import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


# ---------------------------------------------------------------------
# 1️⃣ USER MODEL + MANAGER
# ---------------------------------------------------------------------

class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, max_length=320)
    name = models.CharField(max_length=200)
    password = models.CharField(max_length=128)
    created = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    objects = UserManager()

    def __str__(self):
        return self.name


# ---------------------------------------------------------------------
# 2️⃣ ROOMS
# ---------------------------------------------------------------------

class Room(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField()
    owner = models.ForeignKey(
        User,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="owned_rooms"
    )
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# ---------------------------------------------------------------------
# 3️⃣ MESSAGES
# ---------------------------------------------------------------------

class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="messages")
    user = models.ForeignKey(
        User,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="messages"
    )
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["room", "-created"]),
            models.Index(fields=["user", "-created"]),
        ]
        ordering = ["-created"]

    def __str__(self):
        return f"{self.user} → {self.room}: {self.content[:40]}"


# ---------------------------------------------------------------------
# 4️⃣ ROOM MEMBERS (current members)
# ---------------------------------------------------------------------

class RoomMember(models.Model):
    ROLE_CHOICES = (
        ("owner", "Owner"),
        ("admin", "Admin"),
        ("member", "Member"),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rooms_joined")
    joined_at = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)

    class Meta:
        unique_together = ("room", "user")

    def __str__(self):
        return f"{self.user.name} in {self.room.name}"


# ---------------------------------------------------------------------
# 5️⃣ ROOM MEMBERS LOG (join / leave history)
# ---------------------------------------------------------------------

class RoomMembersLog(models.Model):
    EVENT_CHOICES = [
        ("join", "Join"),
        ("leave", "Leave"),
        ("kick", "Kick"),
        ("invite", "Invite"),
    ]

    id = models.BigAutoField(primary_key=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="member_logs")

    # ✅ FIXED: allow null so join logs without user won't crash
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="membership_logs",
    )

    event_type = models.CharField(max_length=20, choices=EVENT_CHOICES)

    actor = models.ForeignKey(
        User,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="membership_actions"
    )

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        username = self.user.name if self.user else "Unknown"
        return f"{username} {self.event_type} {self.room.name}"
