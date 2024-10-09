from django.shortcuts import render


def homepage(request):
    return render(request, 'home.html', {'home_menu': 'bg-gray-900 text-white'})

