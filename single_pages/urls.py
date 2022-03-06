from django.urls import path
from . import views

urlpatterns=[
    path('about-me/', views.about_me),
    path('', views.landing),
]