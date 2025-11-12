from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.models import Room, RoomMember, Message, RoomMembersLog
import json

User = get_user_model()

# -------------------------------------------------------------------
# LOGIN VIEW (HTML FORM)
# -------------------------------------------------------------------
@csrf_protect
def login_view(request):
    """Handles user login via HTML form."""
    if request.method == "GET":
        return render(request, "login.html")

    email = request.POST.get("email")
    password = request.POST.get("password")

    user = authenticate(request, email=email, password=password)
    if user is None:
        return render(request, "login.html", {"error": "Invalid email or password"})

    login(request, user)

    # ✅ handle both GET and POST next param
    next_url = request.POST.get("next") or request.GET.get("next") or "/rooms/"
    return redirect(next_url)



# -------------------------------------------------------------------
# LOGOUT
# -------------------------------------------------------------------
@require_POST
def logout_view(request):
    logout(request)
    return redirect("/login/")


# -------------------------------------------------------------------
# ROOMS PAGE (HTML)
# -------------------------------------------------------------------
@login_required
def rooms_page(request):
    return render(request, "rooms.html", {"user": request.user})


# -------------------------------------------------------------------
# CHAT PAGE (HTML)
# -------------------------------------------------------------------
@login_required
def chat_page(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    user = request.user

    # Check if user already exists in room
    membership, created = RoomMember.objects.get_or_create(room=room, user=user)

    if created:
        # Detect invite
        is_invite = request.GET.get("invite") == "1"

        RoomMembersLog.objects.create(
            room=room,
            user=user,
            actor=user,
            event_type="invite" if is_invite else "join"
        )

    # Load last messages
    messages = Message.objects.filter(room=room).order_by("-created")[:50]

    return render(
        request,
        "chat.html",
        {"room": room, "messages": reversed(messages), "user": user}
    )




# -------------------------------------------------------------------
# API — LIST USER ROOMS
# -------------------------------------------------------------------
@require_GET
def list_rooms(request):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Unauthorized"}, status=401)

    rooms = RoomMember.objects.filter(user=request.user).select_related("room")
    data = [{"id": str(r.room.id), "name": r.room.name} for r in rooms]
    return JsonResponse({"rooms": data})


# -------------------------------------------------------------------
# API — ROOM MESSAGES
# -------------------------------------------------------------------
@require_GET
def room_messages(request, room_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not logged in"}, status=401)

    try:
        room = Room.objects.get(id=room_id)
    except Room.DoesNotExist:
        return JsonResponse({"error": "Room not found"}, status=404)

    limit = int(request.GET.get("limit", 50))
    messages = Message.objects.filter(room=room).order_by("-created")[:limit]

    data = [{
        "id": str(msg.id),
        "content": msg.content,
        "user": msg.user.name,
        "user_id": str(msg.user.id),
        "created": msg.created.isoformat(),
    } for msg in reversed(messages)]

    return JsonResponse(data, safe=False)


# -------------------------------------------------------------------
# API — ADD USER (INVITE)
# -------------------------------------------------------------------
@require_POST
def add_user(request, room_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not logged in"}, status=401)

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
        return JsonResponse({"error": "User does not exist"}, status=404)

    RoomMember.objects.get_or_create(room=room, user=target)
    return JsonResponse({"detail": f"{target.name} added"})


# -------------------------------------------------------------------
# API — LEAVE ROOM
# -------------------------------------------------------------------
@require_POST
def leave_room(request, room_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not logged in"}, status=401)

    try:
        membership = RoomMember.objects.get(room_id=room_id, user=request.user)
    except RoomMember.DoesNotExist:
        return JsonResponse({"error": "Not in room"}, status=404)

    if membership.room.owner == request.user:
        return JsonResponse({"error": "Owner cannot leave their own room"}, status=400)

    membership.delete()
    return JsonResponse({"detail": "Left room"})


# -------------------------------------------------------------------
# API — MAKE ADMIN
# -------------------------------------------------------------------
@require_POST
def make_admin(request, room_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not logged in"}, status=401)

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


# -------------------------------------------------------------------
# API — CREATE ROOM
# -------------------------------------------------------------------
@require_POST
@login_required
def create_room(request):
    data = json.loads(request.body.decode())
    name = data.get("name")
    if not name:
        return JsonResponse({"error": "Room name required"}, status=400)

    user = request.user
    room = Room.objects.create(name=name, owner=user)
    RoomMember.objects.create(room=room, user=user, is_admin=True)

    RoomMembersLog.objects.create(
        room=room, user=user, actor=user, event_type="join"
    )

    return JsonResponse({
        "id": str(room.id),
        "name": room.name,
        "owner": user.name,
    })


# -------------------------------------------------------------------
# API — GET ROOM MEMBERS
# -------------------------------------------------------------------
@login_required
def get_room_members(request, room_id):
    try:
        room = Room.objects.get(id=room_id)
    except Room.DoesNotExist:
        return JsonResponse({"error": "Room not found"}, status=404)

    members = RoomMember.objects.filter(room=room).select_related("user")
    data = [{
        "id": str(m.user.id),
        "username": m.user.name,
        "email": m.user.email,
        "is_admin": m.is_admin,
    } for m in members]

    return JsonResponse({"members": data})


# -------------------------------------------------------------------
# HOME PAGE (REGISTER)
# -------------------------------------------------------------------
def home_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        username = request.POST.get("username")
        password = request.POST.get("password")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, "home.html")

        user = User.objects.create_user(email=email, name=username, password=password)
        login(request, user)
        return redirect("/rooms/")

    return render(request, "home.html")
