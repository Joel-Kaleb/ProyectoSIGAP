from django.db import models
from projects.models import Proyecto # Importar el proyecto a evaluar
from people.models import Evaluador # Importar quién evalúa

class Evaluaciones(models.Model):
    """
    Registra el historial de revisiones y el dictamen de un proyecto.
    Esta tabla soporta múltiples revisiones para un mismo proyecto.
    """
    # Clave Primaria (PK) autoincrementable para el registro histórico
    id_evaluacion = models.AutoField(primary_key=True, verbose_name="ID DE EVALUACIÓN")
    
    # Claves Foráneas (Relaciones 1:N)
    # 1. ¿Qué proyecto fue evaluado?
    proyecto = models.ForeignKey(
        Proyecto, 
        on_delete=models.CASCADE, 
        verbose_name="PROYECTO EVALUADO"
    )
    # 2. ¿Quién evaluó?
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
        ('FINAL', 'Dictamen Final'), # Para la presentación final
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
        # Asegura que las evaluaciones se ordenen de la más reciente a la más antigua
        ordering = ['-fecha_evaluacion'] 

    def __str__(self):
        return f"Evaluación {self.id_evaluacion} - {self.proyecto.folio} ({self.tipo_revision})"