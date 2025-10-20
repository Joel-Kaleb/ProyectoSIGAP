from django.urls import path 
from . import views

urlpatterns = [
    path('importar/', views.importar_proyectos_view, name='importar_proyectos'), 
]