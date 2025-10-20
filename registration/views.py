# import pandas as pd
# import os
# from django.db import IntegrityError, transaction
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test

# --- Funciones Auxiliares ---
def is_admin(user):
    return user.is_superuser or user.is_staff

# --- Vista Principal ---
@user_passes_test(is_admin)
def importar_proyectos_view(request):
    # La función solo renderiza la plantilla
    return render(request, 'RegistroInicial.html')