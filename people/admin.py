from django.contrib import admin
from .models import Alumno, Asesor, Evaluador

@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo Alumno.
    """
    list_display = ('codigo_estudiante', 'nombre_completo', 'correo_electronico')
    search_fields = ('codigo_estudiante', 'nombre_completo', 'correo_electronico')

@admin.register(Asesor)
class AsesorAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo Asesor.
    """
    list_display = ('codigo_asesor', 'nombre_completo', 'correo_electronico')
    search_fields = ('codigo_asesor', 'nombre_completo', 'correo_electronico')

@admin.register(Evaluador)
class EvaluadorAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo Evaluador.
    """
    list_display = ('codigo_evaluador', 'nombre_completo', 'correo_evaluador', 'especializacion')
    search_fields = ('codigo_evaluador', 'nombre_completo', 'correo_evaluador')
    list_filter = ('especializacion',)
