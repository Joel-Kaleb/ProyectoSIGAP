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
    #autocomplete_fields = ['alumno']

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
    list_display = (
        'folio', 'titulo', 'asesor', 'evaluador', 'modalidad',
        'calendario_registro', 'dictamen',
        'boton_enviar_correo', 'boton_enviar_correo_evaluador'
    )

    list_filter = (
        'modalidad', 'calendario_registro', 'dictamen', 'asesor', 'evaluador'
    )

    search_fields = (
        'folio', 'titulo', 'asesor__nombre_completo',
        'evaluador__nombre_completo', 'participantes__nombre_completo'
    )

    inlines = [
        ParticipacionInline,
        ProrrogaInline,
        EvaluacionesInline
    ]

    # --- Botón personalizado para asesor ---
    def boton_enviar_correo(self, obj):
        return format_html(
            '<a class="button" href="enviar-correo/{}/" '
            'style="padding:5px 10px; background:#0b6efd; color:white; '
            'border-radius:6px; text-decoration:none;">📨 Enviar correo</a>',
            obj.pk
        )
    boton_enviar_correo.short_description = "Acción"

    # --- Botón personalizado para evaluador ---
    def boton_enviar_correo_evaluador(self, obj):
        return format_html(
            '<a class="button" href="enviar-correo-evaluador/{}/" '
            'style="padding:5px 10px; background:#198754; color:white; '
            'border-radius:6px; text-decoration:none;">📧 Enviar a Evaluador</a>',
            obj.pk
        )
    boton_enviar_correo_evaluador.short_description = "Correo Evaluador"

    # --------------------- URLs extras ---------------------
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                'enviar-correo-evaluador/<str:folio>/',
                self.admin_site.admin_view(self.enviar_correo_evaluador),
                name='enviar_correo_evaluador',
            ),
        ]
        return custom_urls + urls

    # --------------------- Lógica del correo ---------------------
    def enviar_correo_evaluador(self, request, folio):
        from django.shortcuts import redirect
        from django.core.mail import send_mail
        from django.conf import settings

        proyecto = Proyecto.objects.get(pk=folio)
        formato1 = Formato1.objects.get(folio=proyecto.folio)
        evaluador = proyecto.evaluador

        if evaluador and evaluador.correo_evaluador:
            send_mail(
                subject="Notificación de Proyecto Asignado",
                message=(
                    f"Estimado/a {evaluador.nombre_completo},\n\n"
                    f"Se le ha asignado el proyecto:\n"
                    f"Folio: {proyecto.folio}\n\n"
                    f" **Introducción:**\n{formato1.introduccion}\n\n"
                    f" **Justificación:**\n{formato1.justificacion}\n\n"
                    f" **Objetivo:**\n{formato1.objetivo}\n\n"
                    f" **Resumen:**\n{formato1.resumen}\n\n"
                    
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[evaluador.correo_evaluador],
                fail_silently=False,
            )

            self.message_user(request, "📧 Correo enviado al evaluador.")
        else:
            self.message_user(request, "❌ El evaluador no tiene correo.", level='error')

        return redirect(f'../../{folio}/change/')



    # --- URL personalizada ---
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('enviar-correo/<str:folio>/', self.admin_site.admin_view(self.enviar_correo), name='enviar_correo'),
            path('enviar-correo-evaluador/<str:folio>/', self.admin_site.admin_view(self.enviar_correo_evaluador), name='enviar_correo_evaluador'),
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


def enviar_correo_evaluador(self, request, folio):
    proyecto = Proyecto.objects.get(pk=folio)

    if not proyecto.evaluador or not proyecto.evaluador.correo_evaluador:
        messages.error(request, "❌ Este proyecto no tiene correo de evaluador registrado.")
        return redirect(request.META.get('HTTP_REFERER', 'admin:index'))

    destinatario = proyecto.evaluador.correo_evaluador

    # Construcción del mensaje con los campos solicitados
    asunto = f"[Evaluación] Información del Proyecto {proyecto.folio}"

    mensaje = (
        f"Estimado evaluador,\n\n"
        f"Se le ha asignado el proyecto con los siguientes datos:\n\n"
        f"• Folio: {proyecto.folio}\n"
        f"• Título: {proyecto.titulo}\n\n"
        f"--- INTRODUCCIÓN ---\n{proyecto.introduccion}\n\n"
        f"--- JUSTIFICACIÓN ---\n{proyecto.justificacion}\n\n"
        f"--- OBJETIVO ---\n{proyecto.objetivo}\n\n"
        f"--- RESUMEN ---\n{proyecto.resumen}\n\n"
        f"Por favor ingrese a SIGAP para continuar con el proceso de evaluación.\n\n"
        f"Atentamente,\n"
        f"Comité de Evaluación"
    )

    send_mail(
        subject=asunto,
        message=mensaje,
        from_email=None,
        recipient_list=[destinatario],
        fail_silently=False,
    )

    messages.success(request, f"✅ Correo enviado al evaluador del proyecto {proyecto.folio}.")
    return redirect(request.META.get('HTTP_REFERER', 'admin:index'))


@admin.register(Participacion)
class ParticipacionAdmin(admin.ModelAdmin):
    list_display = ('proyecto', 'alumno', 'es_representante')
    list_filter = ('es_representante',)
    autocomplete_fields = ['proyecto', 'alumno']


@admin.register(Formato1)
class Formato1Admin(admin.ModelAdmin):
    # 1. Agregamos 'ver_titulo_proyecto' a la lista
    list_display = ('folio', 'ver_titulo_proyecto', 'resumen')
    
    # Buscador para que también busque por el título del proyecto relacionado
    search_fields = ('folio', 'resumen', 'introduccion', 'proyecto__titulo')

    def ver_titulo_proyecto(self, obj):
        
        if hasattr(obj, 'proyecto'):
            return obj.proyecto.titulo
        return "⚠️ Huérfano"

    # 3. Nombre de la columna
    ver_titulo_proyecto.short_description = "Título del Proyecto"
    
    # Ordena la columna por título al darle click
    ver_titulo_proyecto.admin_order_field = 'proyecto__titulo'
