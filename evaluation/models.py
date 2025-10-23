from django.db import models
from projects.models import Proyecto  # Importar el proyecto a evaluar
from people.models import Evaluador   # Importar quién evalúa

class Evaluaciones(models.Model):
    """
    Registra el historial de revisiones y el dictamen de un proyecto.
    Esta tabla soporta múltiples revisiones para un mismo proyecto.
    """
    # Clave Primaria (PK) autoincrementable para el registro histórico
    id_evaluacion = models.AutoField(primary_key=True, verbose_name="ID DE EVALUACIÓN")
    
    # Claves Foráneas (Relaciones 1:N)
    proyecto = models.ForeignKey(
        Proyecto, 
        on_delete=models.CASCADE, 
        verbose_name="PROYECTO EVALUADO"
    )

    evaluador = models.ForeignKey(
        Evaluador, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="EVALUADOR ASIGNADO"
    )
    
    # Atributos de la Evaluación
    fecha_evaluacion = models.DateTimeField(auto_now_add=True, verbose_name="FECHA DE EVALUACIÓN")
    
    # Definición de CHOICES para el estado de la revisión
    REVISION_CHOICES = [
        ('FORMA', 'Revisión de Forma'),
        ('FONDO', 'Revisión de Fondo'),
        ('FINAL', 'Dictamen Final'),
    ]
    
    tipo_revision = models.CharField(
        max_length=10,
        choices=REVISION_CHOICES,
        default='FORMA',
        verbose_name="TIPO DE REVISIÓN"
    )
    
    # Definición de CHOICES para el resolutivo
    RESOLUTIVO_CHOICES = [
        ('APROBADO', 'Aprobado'),
        ('RECHAZADO', 'Rechazado'),
        ('PENDIENTE', 'Pendiente de Correcciones'),
        ('NO_APLICA', 'No Aplica'),
    ]

    resolutivo = models.CharField(
        max_length=20,
        choices=RESOLUTIVO_CHOICES,
        verbose_name="RESOLUTIVO DE LA REVISIÓN"
    )

    observaciones = models.TextField(verbose_name="OBSERVACIONES DETALLADAS")
    
    class Meta:
        verbose_name = "Evaluación Histórica"
        verbose_name_plural = "Evaluaciones Históricas"
        ordering = ['-fecha_evaluacion']

    def save(self, *args, **kwargs):
        """
        Convierte automáticamente a MAYÚSCULAS todos los CharField y TextField
        antes de guardar el registro.
        """
        for field in self._meta.fields:
            if isinstance(field, models.CharField) or isinstance(field, models.TextField):
                valor = getattr(self, field.name)
                if isinstance(valor, str):
                    setattr(self, field.name, valor.upper())
        super().save(*args, **kwargs)

    def __str__(self):
        return f"EVALUACIÓN {self.id_evaluacion} - {self.proyecto.folio} ({self.tipo_revision})"
