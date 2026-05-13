from django.urls import path
from . import views

urlpatterns = [path("", views.index),
               path('Register/', views.Register_view, name='Register'),
]
