from django.urls import path
from . import views

urlpatterns = [path("", views.index),
               path('Register/', views.Register_view, name='Register'),
               path('RegisterArtist', views.RegisterArtist, name='RegisterArtist'),
               path('Login', views.LoginView, name="Login"),
               path('home', views.HomeView, name='home')
]
