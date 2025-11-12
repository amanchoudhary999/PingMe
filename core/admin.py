from django.contrib import admin

# Register your models here.

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Room, Message, RoomMember, RoomMembersLog


# ---------------------------------------------------------------------
# 1️⃣ USER ADMIN
# ---------------------------------------------------------------------

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ("email", "name", "is_staff", "is_superuser", "created")
    list_filter = ("is_staff", "is_superuser", "is_active")
    search_fields = ("email", "name")
    ordering = ("-created",)
    readonly_fields = ("id","created",)

    fieldsets = (
        (None, {"fields": ("email", "name", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")}),
        ("Timestamps", {"fields": ("created",)}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "name", "password1", "password2", "is_staff", "is_active"),
        }),
    )


# ---------------------------------------------------------------------
# 2️⃣ ROOM ADMIN
# ---------------------------------------------------------------------
@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "owner", "created")  # ✅ Added `id`
    search_fields = ("name", "owner__email", "owner__name")
    list_filter = ("created",)
    readonly_fields = ("id", "created") 


# ---------------------------------------------------------------------
# 3️⃣ MESSAGE ADMIN
# ---------------------------------------------------------------------

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("room", "user", "short_content", "created")
    search_fields = ("content", "user__email", "room__name")
    list_filter = ("room", "user", "created")
    readonly_fields = ("created",)

    def short_content(self, obj):
        return (obj.content[:60] + "...") if len(obj.content) > 60 else obj.content
    short_content.short_description = "Message"


# ---------------------------------------------------------------------
# 4️⃣ ROOM MEMBERS ADMIN
# ---------------------------------------------------------------------

@admin.register(RoomMember)
class RoomMemberAdmin(admin.ModelAdmin):
    list_display = ("room", "user", "joined_at")
    search_fields = ("room__name", "user__email", "user__name")
    list_filter = ("room",)
    readonly_fields = ("joined_at",)


# ---------------------------------------------------------------------
# 5️⃣ ROOM MEMBERS LOG ADMIN
# ---------------------------------------------------------------------

@admin.register(RoomMembersLog)
class RoomMembersLogAdmin(admin.ModelAdmin):
    list_display = ("room", "user", "event_type", "actor", "created")
    list_filter = ("event_type", "room", "created")
    search_fields = ("room__name", "user__email", "actor__email")
    readonly_fields = ("created",)
    ordering = ("-created",)

