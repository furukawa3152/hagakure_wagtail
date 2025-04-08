from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.core.exceptions import PermissionDenied
from django.conf import settings

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        """
        Googleログイン時に、許可されたメールアドレスだけ通す
        """
        email = sociallogin.user.email

        # 個別のメールアドレスリストで制限
        if hasattr(settings, "ALLOWED_GOOGLE_EMAILS"):
            if email not in settings.ALLOWED_GOOGLE_EMAILS:
                raise PermissionDenied("このメールアドレスではログインできません")

        # ドメインで制限
        if hasattr(settings, "ALLOWED_GOOGLE_DOMAIN"):
            if not email.endswith(f"@{settings.ALLOWED_GOOGLE_DOMAIN}"):
                raise PermissionDenied("このドメインのメールアドレスのみログイン可能です")

        return True  # 許可されたユーザーはログイン可能