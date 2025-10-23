from django.contrib import admin, messages
from django.core.mail import send_mail
from django.urls import path
from django.shortcuts import redirect
from django.utils.html import format_html
from .models import Proyecto, Formato1, Participacion, Prorroga
from evaluation.models import Evaluaciones


# --- Inlines (Formularios anidados dentro de ProyectoAdmin) ---

class ParticipacionInline(admin.TabularInline):
    model = Participacion
    extra = 1
    autocomplete_fields = ['alumno']

class ProrrogaInline(admin.TabularInline):
    model = Prorroga
    extra = 0

class EvaluacionesInline(admin.TabularInline):
    model = Evaluaciones
    extra = 0
    readonly_fields = ('fecha_evaluacion', 'evaluador', 'tipo_revision', 'resolutivo', 'observaciones')
    can_delete = False


# --- Registros Principales ---

@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = ('folio', 'titulo', 'asesor', 'evaluador', 'modalidad', 'calendario_registro', 'dictamen', 'boton_enviar_correo')
    list_filter = ('modalidad', 'calendario_registro', 'dictamen', 'asesor', 'evaluador')
    search_fields = ('folio', 'titulo', 'asesor__nombre_completo', 'evaluador__nombre_completo', 'participantes__nombre_completo')
    
    inlines = [
        ParticipacionInline,
        ProrrogaInline,
        EvaluacionesInline
    ]
    
    autocomplete_fields = ['asesor', 'evaluador']

    # --- Botón personalizado en el panel ---
    def boton_enviar_correo(self, obj):
        return format_html(
            '<a class="button" href="enviar-correo/{}/" '
            'style="padding:5px 10px; background:#0b6efd; color:white; '
            'border-radius:6px; text-decoration:none;">📨 Enviar correo</a>',
            obj.pk
        )
    boton_enviar_correo.short_description = "Acción"
    boton_enviar_correo.allow_tags = True

    # --- URL personalizada ---
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('enviar-correo/<str:folio>/', self.admin_site.admin_view(self.enviar_correo), name='enviar_correo'),
        ]
        return custom_urls + urls

    # --- Lógica del envío de correo ---
    def enviar_correo(self, request, folio):
        proyecto = Proyecto.objects.get(pk=folio)

        destinatarios = []

        # Correos de asesor y evaluador
        if proyecto.asesor and proyecto.asesor.correo_electronico:
            destinatarios.append(proyecto.asesor.correo_electronico)
        if proyecto.evaluador and proyecto.evaluador.correo_evaluador:
            destinatarios.append(proyecto.evaluador.correo_evaluador)

        # Correos de alumnos participantes
        for participacion in proyecto.participacion_set.all():
            alumno = participacion.alumno
            if alumno and alumno.correo_electronico:
                destinatarios.append(alumno.correo_electronico)

        destinatarios = list(set(destinatarios))  # quitar duplicados

        if not destinatarios:
            messages.error(request, "❌ No hay correos registrados para este proyecto.")
            return redirect(request.META.get('HTTP_REFERER', 'admin:index'))

        # Mensaje del correo
        asunto = f"Notificación del Proyecto {proyecto.folio}"
        mensaje = (
            f"Estimados participantes,\n\n"
            f"Este es un aviso relacionado con el proyecto '{proyecto.titulo}' "
            f"(folio: {proyecto.folio}).\n\n"
            f"Por favor revisen su cuenta SIGAP para más información.\n\n"
            f"Atentamente,\nComité de Evaluación"
        )

        send_mail(
            subject=asunto,
            message=mensaje,
            from_email=None,
            recipient_list=destinatarios,
            fail_silently=False,
        )

        messages.success(request, f"✅ Correo enviado correctamente a los participantes del proyecto {proyecto.folio}.")
        return redirect(request.META.get('HTTP_REFERER', 'admin:index'))


@admin.register(Participacion)
class ParticipacionAdmin(admin.ModelAdmin):
    list_display = ('proyecto', 'alumno', 'es_representante')
    list_filter = ('es_representante',)
    autocomplete_fields = ['proyecto', 'alumno']


@admin.register(Formato1)
class Formato1Admin(admin.ModelAdmin):
    list_display = ('folio', 'resumen')
    search_fields = ('folio', 'resumen', 'introduccion')
