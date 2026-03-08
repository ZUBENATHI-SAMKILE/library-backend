from rest_framework_simplejwt.authentication import JWTAuthentication


class OptionalJWTAuthentication(JWTAuthentication):
    """
    Returns None silently for any token that is not a valid Django JWT.
    This allows AllowAny views to work even when a member token is sent.
    """
    def authenticate(self, request):
        try:
            return super().authenticate(request)
        except Exception:
            return None