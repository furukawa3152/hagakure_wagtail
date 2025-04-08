from wagtail import hooks
from wagtail.admin.menu import MenuItem
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from wagtail.models import Page

@hooks.register("construct_explorer_page_queryset")
def restrict_editor_subpages(parent_page, queryset, request):
    """Editor 権限のユーザーは Blog Page 以外を見れないようにする"""
    if request.user.groups.filter(name="Editor").exists():
        return queryset.filter(content_type__model="blogpage")
    return queryset  # それ以外のユーザーはそのまま