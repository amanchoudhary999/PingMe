from django.urls import path
from core.frontend_views import login_page, rooms_page, chat_page,members_page

urlpatterns = [
    path("login/", login_page, name="login"),
    path("rooms/", rooms_page, name="rooms_page"),
    path("chat/<uuid:room_id>/", chat_page, name="chat_page"),
    path("rooms/<uuid:room_id>/members/", members_page, name="members_page"),
]
