from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed

class JWTAuthFromCookie(JWTAuthentication):
    def authenticate(self, request):
        # Get the access token from cookies
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

            # Attempt to refresh the token if expired
            refresh_token = request.COOKIES.get("refresh_token")
            if not refresh_token:
                print("No refresh token found in cookies.")
                raise AuthenticationFailed("Authentication credentials were not provided.")

            try:
                # Generate a new access token
                new_access_token = RefreshToken(refresh_token).access_token
                return self.get_user(new_access_token), new_access_token
            except TokenError as refresh_error:
                print("Failed to refresh token:", str(refresh_error))
                raise AuthenticationFailed("Invalid refresh token.")

        return None
