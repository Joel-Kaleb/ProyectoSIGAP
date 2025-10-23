from django.contrib import admin
from .models import Evaluaciones
admin.site.site_header = "Panel Administrativo QFB"
admin.site.site_title = "QFB| Administración"
admin.site.index_title = "Gestión de Proyectos Modulares"
admin.site.site_url = None

@admin.register(Evaluaciones)
class EvaluacionesAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo Evaluaciones.
    Permite ver el historial completo de todas las evaluaciones.
    """
    list_display = ('id_evaluacion', 'proyecto', 'evaluador', 'tipo_revision', 'resolutivo', 'fecha_evaluacion')
    list_filter = ('tipo_revision', 'resolutivo', 'evaluador', 'fecha_evaluacion')
    search_fields = ('proyecto__folio', 'evaluador__nombre_completo', 'observaciones')
    
    # Hacemos la fecha de solo lectura porque es auto_now_add
    readonly_fields = ('fecha_evaluacion',)
    
    # Mejora la selección de proyectos y evaluadores
    autocomplete_fields = ['proyecto', 'evaluador']
