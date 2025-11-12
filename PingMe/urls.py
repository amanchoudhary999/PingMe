from django.contrib import admin
from django.urls import path, include
from core.views import login_view,home_view
from core.frontend_views import rooms_page, chat_page

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", login_view),
    path("rooms/", rooms_page),
    path("chat/<uuid:room_id>/", chat_page),

    # ✅ THIS LINE FIXES "Failed to load rooms"
    path("api/", include("core.api.urls")),
    path("", home_view, name="home"),
    
]
