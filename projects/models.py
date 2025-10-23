from django.db import models
# Importar modelos de la app 'people' para las FK
from people.models import Alumno, Asesor, Evaluador 


# ====================================================================
# 1. Formato1 (Relación 1:1)
# ====================================================================

class Formato1(models.Model):
    """Contiene los datos de la documentación inicial del proyecto."""
    folio = models.CharField(max_length=50, primary_key=True, verbose_name="FOLIO PROYECTO") 
    introduccion = models.TextField(verbose_name="INTRODUCCIÓN")
    justificacion = models.TextField(verbose_name="JUSTIFICACIÓN")
    objetivo = models.TextField(verbose_name="OBJETIVO")
    resumen = models.TextField(verbose_name="RESUMEN")
    
    class Meta:
        verbose_name = "Formato Inicial"
        verbose_name_plural = "Formatos Iniciales"
    
    def save(self, *args, **kwargs):
        if self.folio:
            self.folio = self.folio.upper()
        if self.introduccion:
            self.introduccion = self.introduccion.upper()
        if self.justificacion:
            self.justificacion = self.justificacion.upper()
        if self.objetivo:
            self.objetivo = self.objetivo.upper()
        if self.resumen:
            self.resumen = self.resumen.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Formato para Folio: {self.folio}"

# ====================================================================
# 2. Prórroga (Relación 1:N)
# ====================================================================

class Prorroga(models.Model):
    """Registra las solicitudes de prórroga para un proyecto."""
    id_prorroga = models.AutoField(primary_key=True, verbose_name="ID DE PRÓRROGA")
    proyecto = models.ForeignKey(
        'Proyecto',
        on_delete=models.CASCADE,
        verbose_name="PROYECTO"
    )
    justificacion = models.TextField(verbose_name="JUSTIFICACIÓN DE PRÓRROGA")
    calendario_presentacion = models.CharField(max_length=10, verbose_name="CALENDARIO PARA PRESENTACIÓN")

    class Meta:
        verbose_name = "Prórroga"
        verbose_name_plural = "Prórrogas"

    def save(self, *args, **kwargs):
        if self.justificacion:
            self.justificacion = self.justificacion.upper()
        if self.calendario_presentacion:
            self.calendario_presentacion = self.calendario_presentacion.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Prórroga {self.id_prorroga} para {self.proyecto.folio}"

# ====================================================================
# 3. Proyecto (Entidad Central)
# ====================================================================

class Proyecto(models.Model):
    MODALIDAD_CHOICES = [
        ('TRABAJO DE INVESTIGACION', 'TRABAJO DE INVESTIGACION'),
        ('MATERIALES EDUCATIVOS', 'MATERIALES EDUCATIVOS'),
        ('PROTOTIPO', 'PROTOTIPO'),
        ('REPORTE', 'REPORTE'),
        ('VINCULACION SOCIAL', 'VINCULACION SOCIAL'),
    ]
    
    folio = models.CharField(max_length=50, primary_key=True, verbose_name="FOLIO DE PROYECTO")
    titulo = models.CharField(max_length=255, verbose_name="TÍTULO DEL PROYECTO")
    asesor = models.ForeignKey(Asesor, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="ASESOR ASIGNADO")
    evaluador = models.ForeignKey(Evaluador, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="EVALUADOR ASIGNADO")
    formato1 = models.OneToOneField(Formato1, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="DATOS FORMATO 1")
    modalidad = models.CharField(max_length=50, choices=MODALIDAD_CHOICES, verbose_name="MODALIDAD")
    variante = models.CharField(max_length=50, null=True, blank=True, verbose_name="VARIANTE DE MODALIDAD")
    nivel_competencia = models.CharField(max_length=30, null=True, blank=True, verbose_name="MÓDULOS REGISTRADOS")
    dictamen = models.CharField(max_length=50, default='PENDIENTE', verbose_name="DICTAMEN FINAL")
    calendario_registro = models.CharField(max_length=10, verbose_name="CALENDARIO")
    evidencia_url = models.URLField(max_length=500, null=True, blank=True, verbose_name="URL EVIDENCIA PRINCIPAL")
    protocolo_dictamen_url = models.URLField(max_length=500, null=True, blank=True, verbose_name="URL PROTOCOLO DICTAMINADO")
    participantes = models.ManyToManyField(Alumno, through='Participacion', verbose_name="PARTICIPANTES")

    class Meta:
        verbose_name = "Proyecto Modular"
        verbose_name_plural = "Proyectos Modulares"
        
    def save(self, *args, **kwargs):
        if self.folio:
            self.folio = self.folio.upper()
        if self.titulo:
            self.titulo = self.titulo.upper()
        if self.variante:
            self.variante = self.variante.upper()
        if self.nivel_competencia:
            self.nivel_competencia = self.nivel_competencia.upper()
        if self.dictamen:
            self.dictamen = self.dictamen.upper()
        if self.calendario_registro:
            self.calendario_registro = self.calendario_registro.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.folio} - {self.titulo}"

# ====================================================================
# 4. Participacion (Tabla de Unión M:M)
# ====================================================================

class Participacion(models.Model):
    """Tabla de unión que resuelve la relación M:M entre Proyecto y Alumno."""
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    es_representante = models.BooleanField(default=False, verbose_name="ES REPRESENTANTE")

    class Meta:
        unique_together = ('proyecto', 'alumno')
        verbose_name = "Participación en Proyecto"
        verbose_name_plural = "Participaciones en Proyectos"

    def __str__(self):
        rol = "REPRESENTANTE" if self.es_representante else "PARTICIPANTE"
        return f"{self.proyecto.folio} - {self.alumno.codigo_estudiante} ({rol})"
