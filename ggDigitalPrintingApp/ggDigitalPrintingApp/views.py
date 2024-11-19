from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def homepage(request):
    return render(request, 'home.html', {'home_menu': 'bg-gray-900 text-white'})


def access_denied(request):
    return render(request, 'errors/access_denied.html')


def custom_403(request, exception=None):
    return render(request, 'errors/403.html', status=403)


def custom_404(request, exception=None):
    return render(request, 'errors/404.html', status=404)


def custom_500(request):
    return render(request, 'errors/500.html', status=500)
