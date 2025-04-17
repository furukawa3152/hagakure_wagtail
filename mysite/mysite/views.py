# CMS以外
from django.shortcuts import render

# loginページ
def blog_login(request):
    return render(request, 'mysite/blog_login.html')

# 404ページテスト用
from django.shortcuts import render
def test_404(request):
    return render(request, '404.html', status=404)