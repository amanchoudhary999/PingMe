from django.contrib.auth import get_user_model
from rest_framework import serializers
from core.models import Room, Message, RoomMember

User = get_user_model()


class UserPublicSerializer(serializers.ModelSerializer):
    """Minimal public info for users."""

    class Meta:
        model = User
        fields = ["id", "email", "name", "created"]


class RegisterSerializer(serializers.ModelSerializer):
    """Used for user registration."""
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["id", "email", "name", "password"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data, password=password)
        return user


class RoomSerializer(serializers.ModelSerializer):
    """Basic room serializer with owner details."""
    owner = UserPublicSerializer(read_only=True)

    class Meta:
        model = Room
        fields = ["id", "name", "owner", "created"]


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for messages in a room."""
    user = UserPublicSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ["id", "room", "user", "content", "created"]
        read_only_fields = ["id", "user", "created"]


class RoomMemberSerializer(serializers.ModelSerializer):
    """Serializer for room membership."""
    user = UserPublicSerializer(read_only=True)

    class Meta:
        model = RoomMember
        fields = ["id", "room", "user", "joined_at"]
        read_only_fields = ["id", "joined_at"]
