import jwt
from django.contrib.auth.models import User
from rest_framework import authentication
from rest_framework import exceptions
from django.conf import settings

class SupabaseJWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return None

        try:
            token_type, token = auth_header.split(' ')
            if token_type.lower() != 'bearer':
                return None
        except ValueError:
            raise exceptions.AuthenticationFailed('Invalid token header. Use "Bearer <token>".')

        try:
            payload = jwt.decode(
                token, 
                settings.SUPABASE_JWT_SECRET, 
                algorithms=["HS256"], 
                options={"verify_aud": False}
            )
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired.')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Invalid token.')

        supabase_uid = payload.get('sub')
        email = payload.get('email')
        
        if not supabase_uid:
            raise exceptions.AuthenticationFailed('User identifier missing from token.')

        user, created = User.objects.get_or_create(
            username=supabase_uid, 
            defaults={'email': email}
        )

        if created:
            print(f"🎉 New Tuk-Tuk driver registered with username/UID: {user.username}")

        return (user, None)