from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from core.models import Room, RoomMember, Message, User
import json


# -------------------------------------------------------------------
# CSRF COOKIE
# -------------------------------------------------------------------
@ensure_csrf_cookie
def get_csrf(request):
    """Sets CSRF cookie for frontend apps."""
    return JsonResponse({"detail": "CSRF cookie set"})


# -------------------------------------------------------------------
# LOGIN / LOGOUT
# -------------------------------------------------------------------
@csrf_protect
@require_POST
def login_view(request):
    """Handles login for API clients (AJAX/JS-based)."""
    data = json.loads(request.body.decode() or "{}")
    email = data.get("email")
    password = data.get("password")

    user = authenticate(request, email=email, password=password)
    if user is None:
        return JsonResponse({"detail": "Invalid credentials"}, status=400)

    login(request, user)
    return JsonResponse({"detail": "Login successful"})


@require_POST
def logout_view(request):
    """Logs out user."""
    logout(request)
    return JsonResponse({"detail": "Logged out"})


# -------------------------------------------------------------------
# ROOMS — CRUD + MEMBERS
# -------------------------------------------------------------------
@login_required
@require_GET
def list_rooms(request):
    """Returns all rooms the user is a member of."""
    rooms = RoomMember.objects.filter(user=request.user).select_related("room")
    data = [{"id": str(r.room.id), "name": r.room.name} for r in rooms]
    return JsonResponse({"rooms": data})


@login_required
@require_POST
def create_room(request):
    """Creates a new chat room."""
    data = json.loads(request.body.decode())
    name = data.get("name")

    if not name:
        return JsonResponse({"error": "Room name required"}, status=400)

    room = Room.objects.create(name=name, owner=request.user)
    RoomMember.objects.create(room=room, user=request.user, is_admin=True)
    return JsonResponse({"id": str(room.id), "name": room.name})


@login_required
@require_GET
def room_messages(request, room_id):
    """Fetches messages for a room."""
    try:
        room = Room.objects.get(id=room_id)
    except Room.DoesNotExist:
        return JsonResponse({"error": "Room not found"}, status=404)

    limit = int(request.GET.get("limit", 50))
    messages = Message.objects.filter(room=room).order_by("-created")[:limit]

    data = [{
        "id": str(m.id),
        "user": m.user.name,
        "content": m.content,
        "created": m.created.isoformat(),
    } for m in reversed(messages)]

    return JsonResponse(data, safe=False)


@login_required
@require_GET
def get_room_members(request, room_id):
    """Returns members of a given room."""
    try:
        room = Room.objects.get(id=room_id)
    except Room.DoesNotExist:
        return JsonResponse({"error": "Room not found"}, status=404)

    # Fetch members
    members = RoomMember.objects.filter(room=room).select_related("user")

    data = [{
        "id": str(m.user.id),
        "username": m.user.name,
        "email": m.user.email,
        "is_admin": m.is_admin,
    } for m in members]

    # OWNER is admin in your logic
    current_user_is_admin = RoomMember.objects.filter(
        room=room, user=request.user, is_admin=True
    ).exists()

    return JsonResponse({
        "members": data,
        "current_user_id": request.user.id,
        "current_user_is_admin": current_user_is_admin,
    })


# -------------------------------------------------------------------
# ROOM ACTIONS — ADD / KICK / LEAVE / MAKE ADMIN
# -------------------------------------------------------------------
@login_required
@require_POST
def add_user(request, room_id):
    """Owner adds user to room by email."""
    email = request.POST.get("email")
    if not email:
        return JsonResponse({"error": "Email required"}, status=400)

    try:
        room = Room.objects.get(id=room_id)
    except Room.DoesNotExist:
        return JsonResponse({"error": "Room not found"}, status=404)

    if room.owner != request.user:
        return JsonResponse({"error": "Only owner can invite"}, status=403)

    try:
        target = User.objects.get(email=email)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    RoomMember.objects.get_or_create(room=room, user=target)
    return JsonResponse({"detail": f"{target.name} added"})


@login_required
@require_POST
def kick_user(request, room_id):
    """Removes a user from a room (owner only)."""
    user_id = request.POST.get("user_id")
    if not user_id:
        return JsonResponse({"error": "user_id required"}, status=400)

    try:
        room = Room.objects.get(id=room_id)
    except Room.DoesNotExist:
        return JsonResponse({"error": "Room not found"}, status=404)

    if room.owner != request.user:
        return JsonResponse({"error": "Only owner can kick"}, status=403)

    RoomMember.objects.filter(room=room, user_id=user_id).delete()
    return JsonResponse({"detail": "User removed"})


@login_required
@require_POST
def leave_room(request, room_id):
    """Allows a user to leave a room."""
    try:
        membership = RoomMember.objects.get(room_id=room_id, user=request.user)
    except RoomMember.DoesNotExist:
        return JsonResponse({"error": "Not in room"}, status=404)

    if membership.room.owner == request.user:
        return JsonResponse({"error": "Owner cannot leave their own room"}, status=400)

    membership.delete()
    return JsonResponse({"detail": "Left room"})


@login_required
@require_POST
def make_admin(request, room_id):
    """Transfers room ownership."""
    target_id = request.POST.get("user_id")
    if not target_id:
        return JsonResponse({"error": "user_id required"}, status=400)

    try:
        room = Room.objects.get(id=room_id)
    except Room.DoesNotExist:
        return JsonResponse({"error": "Room not found"}, status=404)

    if room.owner != request.user:
        return JsonResponse({"error": "Only owner can promote"}, status=403)

    new_owner = User.objects.get(id=target_id)
    room.owner = new_owner
    room.save()
    return JsonResponse({"detail": f"{new_owner.name} is now admin"})
