from django.db import models
# Importar modelos de la app 'people' para las FK
from people.models import Alumno, Asesor, Evaluador 


# ====================================================================
# 1. Formato1 (Relación 1:1)
# ====================================================================

class Formato1(models.Model):
    """Contiene los datos de la documentación inicial del proyecto."""
    # PK: El folio es la PK para asegurar la relación 1:1 con Proyecto
    folio = models.CharField(max_length=50, primary_key=True, verbose_name="FOLIO PROYECTO") 
    introduccion = models.TextField(verbose_name="INTRODUCCIÓN")
    justificacion = models.TextField(verbose_name="JUSTIFICACIÓN")
    objetivo = models.TextField(verbose_name="OBJETIVO")
    resumen = models.TextField(verbose_name="RESUMEN")
    
    class Meta:
        verbose_name = "Formato Inicial"
        verbose_name_plural = "Formatos Iniciales"
    
    def __str__(self):
        return f"Formato para Folio: {self.folio}"

# ====================================================================
# 2. Prórroga (Relación 1:N)
# ====================================================================

class Prorroga(models.Model):
    """Registra las solicitudes de prórroga para un proyecto."""
    id_prorroga = models.AutoField(primary_key=True, verbose_name="ID DE PRÓRROGA")
    
    # FK: Proyecto al que se aplica la prórroga
    proyecto = models.ForeignKey(
        'Proyecto', # Se usa string porque 'Proyecto' aún no está definido
        on_delete=models.CASCADE,
        verbose_name="PROYECTO"
    )
    
    justificacion = models.TextField(verbose_name="JUSTIFICACIÓN DE PRÓRROGA")
    calendario_presentacion = models.CharField(max_length=10, verbose_name="CALENDARIO PARA PRESENTACIÓN")

    class Meta:
        verbose_name = "Prórroga"
        verbose_name_plural = "Prórrogas"

    def __str__(self):
        return f"Prórroga {self.id_prorroga} para {self.proyecto.folio}"

# ====================================================================
# 3. Proyecto (Entidad Central)
# ====================================================================

class Proyecto(models.Model):
    # Definición de CHOICES para la Modalidad
    MODALIDAD_CHOICES = [
        ('TRABAJO DE INVESTIGACIÓN', 'TRABAJO DE INVESTIGACIÓN'),
        ('MATERIALES EDUCATIVOS', 'MATERIALES EDUCATIVOS'),
        ('PROTOTIPO', 'PROTOTIPO'),
        ('REPORTE', 'REPORTE'),
        ('VINCULACIÓN SOCIAL', 'PROYECTOS DE VINCULACIÓN SOCIAL'),
    ]
    
    # PK: Folio compuesto (ej. 218466066-2025B)
    folio = models.CharField(max_length=50, primary_key=True, verbose_name="FOLIO DE PROYECTO")
    titulo = models.CharField(max_length=255, verbose_name="TÍTULO DEL PROYECTO")
    
    # Claves Foráneas (1:N y 1:1)
    asesor = models.ForeignKey(Asesor, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="ASESOR ASIGNADO")
    evaluador = models.ForeignKey(Evaluador, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="EVALUADOR ASIGNADO")
    formato1 = models.OneToOneField(Formato1, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="DATOS FORMATO 1")
    
    # Atributos del proyecto
    modalidad = models.CharField(max_length=50, choices=MODALIDAD_CHOICES, verbose_name="MODALIDAD")
    nivel_competencia = models.CharField(max_length=20, verbose_name="VARIANTE DE MODALIDAD")
    dictamen = models.CharField(max_length=50, verbose_name="DICTAMEN FINAL")
    calendario_registro = models.CharField(max_length=10, verbose_name="CALENDARIO")
    
    # URLs de Drive
    evidencia_url = models.URLField(max_length=500, verbose_name="URL EVIDENCIA PRINCIPAL")
    protocolo_dictamen_url = models.URLField(max_length=500, verbose_name="URL PROTOCOLO DICTAMINADO")
    evidencia_adicional_url = models.URLField(max_length=500, null=True, blank=True, verbose_name="URL EVIDENCIA ADICIONAL")

    # Relación M:M explícita a través de una tabla intermedia
    participantes = models.ManyToManyField(Alumno, through='Participacion', verbose_name="PARTICIPANTES")

    class Meta:
        verbose_name = "Proyecto Modular"
        verbose_name_plural = "Proyectos Modulares"
        
    def __str__(self):
        return f"{self.folio} - {self.titulo}"

# ====================================================================
# 4. Participacion (Tabla de Unión M:M)
# ====================================================================

class Participacion(models.Model):
    """Tabla de unión que resuelve la relación M:M entre Proyecto y Alumno."""
    # Claves Compuestas del M:M
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    
    # Atributo propio de la relación (el rol de representante)
    es_representante = models.BooleanField(default=False, verbose_name="ES REPRESENTANTE")

    class Meta:
        unique_together = ('proyecto', 'alumno')
        verbose_name = "Participación en Proyecto"
        verbose_name_plural = "Participaciones en Proyectos"

    def __str__(self):
        rol = "Representante" if self.es_representante else "Participante"
        return f"{self.proyecto.folio} - {self.alumno.codigo_estudiante} ({rol})"