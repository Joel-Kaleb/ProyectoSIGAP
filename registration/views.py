import pandas as pd
import os
from decouple import config
# from django.db import IntegrityError, transaction
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
import logging
from datetime import date

logger = logging.getLogger(__name__)

RUTA_PROCESADOS = config('RUTA_PROCESADOS')

# --- Funciones Auxiliares ---
def is_admin(user):
    return user.is_superuser or user.is_staff

# --- Vista Principal ---
@user_passes_test(is_admin)
def importar_proyectos_view(request):

    fecha_actual = date.today()
    año_actual = fecha_actual.year
    mes_actual = fecha_actual.month

    calendario_actual = str(año_actual) + ("A" if mes_actual < 7 else "B")
    
    NOMBRE_ARCHIVO_BASE = "FORMATO1- (Respuestas).xlsx"

    nombre_archivo_final = NOMBRE_ARCHIVO_BASE.replace('- ', f'-{calendario_actual} ')

    RUTA_COMPLETA = os.path.join(
        RUTA_PROCESADOS, 
        str(año_actual) + ('A' if mes_actual < 7 else 'B'), 
        '1-Procesados', 
        nombre_archivo_final
    )

    return render(request, 'RegistroInicial.html')