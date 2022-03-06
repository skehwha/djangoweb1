from django.shortcuts import render

def landing(request):
    return render(request, 'single_pages/landing.html')

def about_me(requset):
    return render(requset, 'single_pages/about_me.html')