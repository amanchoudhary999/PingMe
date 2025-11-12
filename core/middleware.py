from urllib.parse import parse_qs
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.models import Session
from channels.middleware import BaseMiddleware

User = get_user_model()


class SessionAuthMiddleware(BaseMiddleware):
    """
    Custom middleware that extracts sessionid from cookies,
    loads the Django user, and attaches it to scope["user"].
    """

    async def __call__(self, scope, receive, send):
        headers = dict(scope.get("headers", []))
        cookies = {}

        # Extract Cookie header
        if b"cookie" in headers:
            cookie_header = headers[b"cookie"].decode()
            for part in cookie_header.split(";"):
                if "=" in part:
                    k, v = part.strip().split("=", 1)
                    cookies[k] = v

        session_key = cookies.get("sessionid")

        # Load user from session
        if session_key:
            try:
                session = Session.objects.get(session_key=session_key)
                uid = session.get_decoded().get("_auth_user_id")
                scope["user"] = User.objects.get(id=uid)
            except Exception:
                scope["user"] = AnonymousUser()
        else:
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)
