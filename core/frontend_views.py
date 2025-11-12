from django.shortcuts import render, get_object_or_404,redirect
from core.models import Room,RoomMembersLog,Message
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required

@csrf_protect
def login_page(request):
    if request.method == "GET":
        next_url = request.GET.get("next", "")
        return render(request, "login.html", {"next": next_url})

    # POST (login)
    email = request.POST.get("email")
    password = request.POST.get("password")
    next_url = request.POST.get("next") or "/rooms/"

    user = authenticate(request, email=email, password=password)
    if not user:
        return render(request, "login.html", {"error": "Invalid login", "next": next_url})

    login(request, user)
    return redirect(next_url)

def rooms_page(request):
    return render(request, "rooms.html")

@login_required
def chat_page(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    user = request.user

    # Create membership
    membership, created = RoomMember.objects.get_or_create(room=room, user=user)

    if created:
        event_type = "invite" if request.GET.get("invite") == "1" else "join"
        RoomMembersLog.objects.create(
            room=room,
            user=user,
            actor=user,
            event_type=event_type
        )

    messages = Message.objects.filter(room=room).order_by("-created")[:50]

    return render(
        request, 
        "chat.html",
        {"room": room, "messages": reversed(messages), "user": user}
    )

from django.shortcuts import render, get_object_or_404
from .models import Room, RoomMember

def members_page(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    members = RoomMember.objects.filter(room=room).select_related("user")

    return render(request, "members.html", {
        "room": room,
        "members": members,
    })

