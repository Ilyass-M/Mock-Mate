from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

class JWTAuthFromCookie(JWTAuthentication):
    def authenticate(self, request):
        # Try to get token from cookie
        raw_token = request.COOKIES.get("access_token")
        print("Raw token from cookie:", raw_token)

        # Fallback to Authorization header
        if raw_token is None:
            auth_header = request.META.get("HTTP_AUTHORIZATION")
            if auth_header and auth_header.startswith("Bearer "):
                raw_token = auth_header.split(" ")[1]

        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token
        except (InvalidToken, TokenError) as e:
            print("Invalid or expired token:", str(e))
            return None
