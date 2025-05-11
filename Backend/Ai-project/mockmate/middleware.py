from channels.middleware import BaseMiddleware
from urllib.parse import parse_qs
import jwt

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        from django.contrib.auth.models import AnonymousUser  # Lazy import
        
        from AiQuetionare.models import CustomUser as User  # Lazy import
        from django.conf import settings
        from channels.db import database_sync_to_async

        # Extract token from query string (e.g., ws://...?token=XYZ)
        query_string = scope.get("query_string", b"").decode()
        query_params = parse_qs(query_string)
        token_list = query_params.get("token")

        if token_list:
            token = token_list[0]  # First value in case multiple tokens

            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                user_id = payload.get("user_id")
                # print(f"Decoded user_id: {user_id}")
                @database_sync_to_async
                def get_user():
                    try:
                        return User.objects.get(id=user_id)
                    except User.DoesNotExist:
                        return AnonymousUser()

                scope["user"] = await get_user()

            except Exception as e:
                scope["user"] = AnonymousUser()
        else:
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)
