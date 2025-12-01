from rest_framework import authentication
from rest_framework import exceptions
from django.utils import timezone
from .models import AccessToken


class TokenAuthentication(authentication.BaseAuthentication):
    """自定义Token认证"""
    
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header:
            return None
        
        try:
            auth_type, token = auth_header.split(' ', 1)
            if auth_type.lower() != 'bearer':
                return None
        except ValueError:
            return None
        
        try:
            access_token = AccessToken.objects.select_related('user').get(
                token=token,
                is_active=True
            )
        except AccessToken.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token')
        
        # 检查是否过期
        if access_token.expires_at < timezone.now():
            access_token.is_active = False
            access_token.save()
            raise exceptions.AuthenticationFailed('Token expired')
        
        return (access_token.user, access_token)
    
    def authenticate_header(self, request):
        return 'Bearer'

