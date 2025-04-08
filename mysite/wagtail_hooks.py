from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from allauth.socialaccount.models import SocialAccount
from wagtail import hooks
@hooks.register("construct_wagtail_userbar")
def google_login_button(request, items):
    if not request.user.is_authenticated:
        items.append({
            "name": "Googleでログインする",
            "url": "/accounts/google/login/",
            "classname": "icon icon-user",
        })

@hooks.register("before_serve_page")
def auto_add_user_to_admin_group(request, page):
    user = request.user
    if user.is_authenticated:
        social_account = SocialAccount.objects.filter(user=user, provider="google").first()
        if social_account:
            user.is_staff = True
            user.save()

            # 「管理者グループ」に追加（あらかじめ作成されている必要あり）
            admin_group, created = Group.objects.get_or_create(name="Editors")
            user.groups.add(admin_group)
            print(user.groups.all())  # どのグループに属しているか確認
