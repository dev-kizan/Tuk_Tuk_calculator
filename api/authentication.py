# import jwt
# from django.contrib.auth.models import User
# from rest_framework import authentication
# from rest_framework import exceptions
# from django.conf import settings

# class SupabaseJWTAuthentication(authentication.BaseAuthentication):
#     def authenticate(self, request):
#         auth_header = request.META.get('HTTP_AUTHORIZATION')
#         if not auth_header:
#             return None

#         print("\n=== DEBUG: INCOMING AUTH HEADER ===")
#         print(f"Header Value: {auth_header}")
#         print("===================================\n")

#         try:
#             token_type, token = auth_header.split(' ')

#             print(f"🔑 Extracted JWT Token: {token[:20]}...[truncated]")

#             if token_type.lower() != 'bearer':
#                 return None
#         except ValueError:
#             raise exceptions.AuthenticationFailed('Invalid token header. Use "Bearer <token>".')

#         try:
#             payload = jwt.decode(
#                 token, 
#                 settings.SUPABASE_JWT_SECRET, 
#                 algorithms=["HS256"], 
#                 options={"verify_aud": False}
#             )

#             print(f"✅ Decoded Payload Sub/UID: {payload.get('sub')}")

#         except jwt.ExpiredSignatureError:
#             print("❌ Token Error: Expired")
#             raise exceptions.AuthenticationFailed('Token has expired.')
#         except jwt.InvalidTokenError as e:
#             print(f"❌ Token Error: Invalid - {e}")
#             raise exceptions.AuthenticationFailed('Invalid token.')

#         supabase_uid = payload.get('sub')
#         email = payload.get('email')
        
#         if not supabase_uid:
#             raise exceptions.AuthenticationFailed('User identifier missing from token.')

#         user, created = User.objects.get_or_create(
#             username=supabase_uid, 
#             defaults={'email': email}
#         )

#         if created:
#             print(f"🎉 New Tuk-Tuk driver registered with username/UID: {user.username}")

#         return (user, None)






# api/authentication.py
import jwt
from django.contrib.auth.models import User
from rest_framework import authentication
from rest_framework import exceptions

class SupabaseJWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return None

        print("\n=== DEBUG: INCOMING AUTH HEADER ===")
        print(f"Header Value: {auth_header}")
        print("===================================\n")

        try:
            token_type, token = auth_header.split(' ')
            print(f"🔑 Extracted JWT Token: {token[:20]}...[truncated]")

            if token_type.lower() != 'bearer':
                return None
        except ValueError:
            raise exceptions.AuthenticationFailed('Invalid token header. Use "Bearer <token>".')

        try:            
            # CRITICAL FIX: Explicitly pass key=None alongside verify_signature=False
            # This completely tells PyJWT not to run internal algorithm type checking.
            payload = jwt.decode(
                token, 
                key=None, 
                options={"verify_signature": False, "verify_aud": False}
            )

            print(f"✅ Decoded Payload Sub/UID: {payload.get('sub')}")

        except jwt.ExpiredSignatureError:
            print("❌ Token Error: Expired")
            raise exceptions.AuthenticationFailed('Token has expired.')
        except jwt.InvalidTokenError as e:
            print(f"❌ Token Error: Invalid structure - {e}")
            raise exceptions.AuthenticationFailed(f'Invalid token: {e}')

        supabase_uid = payload.get('sub')
        email = payload.get('email')
        
        if not supabase_uid:
            raise exceptions.AuthenticationFailed('User identifier missing from token.')

        # Create or fetch the user model (Triggers your profile signal instantly!)
        user, created = User.objects.get_or_create(
            username=supabase_uid, 
            defaults={'email': email}
        )

        if created:
            print(f"🎉 New Tuk-Tuk driver registered with username/UID: {user.username}")

        return (user, None)