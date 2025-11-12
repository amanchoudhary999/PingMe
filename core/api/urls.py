from django.urls import path
from .views import (
    get_csrf,
    login_view,
    logout_view,
    list_rooms,
    room_messages,
    get_room_members,
    add_user,
    kick_user,
    leave_room,
    make_admin,
    create_room,
)

urlpatterns = [
    # Auth
    path("auth/csrf/", get_csrf, name="get-csrf"),
    path("auth/login/", login_view, name="login"),
    path("auth/logout/", logout_view, name="logout"),

    # Rooms
    path("rooms/list/", list_rooms, name="list_rooms"),
    path("rooms/create/", create_room, name="create_room"),
    path("rooms/<uuid:room_id>/messages/", room_messages, name="room_messages"),
    path("rooms/<uuid:room_id>/members/", get_room_members, name="get_room_members"),

    # Room Actions
    path("rooms/<uuid:room_id>/add/", add_user, name="add_user"),
    path("rooms/<uuid:room_id>/kick/", kick_user, name="kick_user"),
    path("rooms/<uuid:room_id>/leave/", leave_room, name="leave_room"),
    path("rooms/<uuid:room_id>/make-admin/", make_admin, name="make_admin"),
]
