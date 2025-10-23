from django.contrib import admin
from .models import Proyecto, Formato1, Participacion, Prorroga
# Importamos modelos de otras apps para los 'inlines'
from evaluation.models import Evaluaciones 

# --- Inlines (Formularios anidados dentro de ProyectoAdmin) ---

class ParticipacionInline(admin.TabularInline):
    """
    Permite agregar/editar Participantes (Alumnos) directamente 
    desde la vista de un Proyecto.
    """
    model = Participacion
    extra = 1 # Espacios para agregar 1 nuevo participante por defecto
    autocomplete_fields = ['alumno'] # Mejora la selección de alumnos

class ProrrogaInline(admin.TabularInline):
    """
    Permite ver y agregar Prórrogas directamente desde 
    la vista de un Proyecto.
    """
    model = Prorroga
    extra = 0 # No mostrar prórrogas vacías por defecto

class EvaluacionesInline(admin.TabularInline):
    """
    Permite ver el historial de Evaluaciones directamente 
    desde la vista de un Proyecto.
    (Importado de la app 'evaluation')
    """
    model = Evaluaciones
    extra = 0 # No mostrar evaluaciones vacías
    readonly_fields = ('fecha_evaluacion', 'evaluador', 'tipo_revision', 'resolutivo', 'observaciones')
    can_delete = False

# 🚨 SE ELIMINÓ LA CLASE 'Formato1Inline' PORQUE LA RELACIÓN O2O
# ESTÁ EN EL MODELO 'Proyecto' Y NO EN 'Formato1'.

# --- Registros Principales ---

@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    """
    Configuración principal para el modelo Proyecto.
    """
    list_display = ('folio', 'titulo', 'asesor', 'evaluador', 'modalidad', 'calendario_registro', 'dictamen')
    list_filter = ('modalidad', 'calendario_registro', 'dictamen', 'asesor', 'evaluador')
    search_fields = ('folio', 'titulo', 'asesor__nombre_completo', 'evaluador__nombre_completo', 'participantes__nombre_completo')
    
    # Aquí conectamos todos los formularios anidados
    inlines = [
        ParticipacionInline,
        ProrrogaInline,
        EvaluacionesInline 
        # 🚨 SE ELIMINÓ 'Formato1Inline' DE ESTA LISTA
    ]
    
    autocomplete_fields = ['asesor', 'evaluador'] # Facilita la asignación

@admin.register(Participacion)
class ParticipacionAdmin(admin.ModelAdmin):
    """
    Registro individual del modelo Participacion.
    Útil para ver todas las participaciones de golpe.
    """
    list_display = ('proyecto', 'alumno', 'es_representante')
    list_filter = ('es_representante',)
    autocomplete_fields = ['proyecto', 'alumno']

@admin.register(Formato1)
class Formato1Admin(admin.ModelAdmin):
    """
    Registro individual para Formato1.
    No se puede usar como 'inline' porque la relación OneToOne
    está definida en 'Proyecto' (apuntando a Formato1) y no
    al revés.
    """
    list_display = ('folio', 'resumen')
    search_fields = ('folio', 'resumen', 'introduccion')

# No registramos Prorroga por separado, 
# ya que es más intuitivo manejarlo desde el Proyecto.