from django.db import models

# ====================================================================
# 1. Alumno (Participante)
# ====================================================================

class Alumno(models.Model):
    """Modelo para los estudiantes participantes de los proyectos."""
    codigo_estudiante = models.CharField(max_length=9, primary_key=True, verbose_name="CÓDIGO DE ESTUDIANTE")
    nombre_completo = models.CharField(max_length=200, verbose_name="NOMBRE COMPLETO")
    correo_electronico = models.EmailField(max_length=100, null=True, blank=True, verbose_name="CORREO ELECTRÓNICO")

    class Meta:
        verbose_name = "Alumno (Participante)"
        verbose_name_plural = "Alumnos (Participantes)"

    def save(self, *args, **kwargs):
        # Convierte los campos a mayúsculas antes de guardar
        if self.codigo_estudiante:
            self.codigo_estudiante = self.codigo_estudiante.upper()
        if self.nombre_completo:
            self.nombre_completo = self.nombre_completo.upper()
        if self.correo_electronico:
            self.correo_electronico = self.correo_electronico.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.codigo_estudiante} - {self.nombre_completo}"

# ====================================================================
# 2. Asesor
# ====================================================================

class Asesor(models.Model):
    """Modelo para los profesores que asesoran el proyecto."""
    codigo_asesor = models.CharField(max_length=20, primary_key=True, verbose_name="CÓDIGO DE ASESOR")
    nombre_completo = models.CharField(max_length=200, verbose_name="NOMBRE COMPLETO")
    correo_electronico = models.EmailField(verbose_name="CORREO ELECTRÓNICO")
    
    class Meta:
        verbose_name = "Asesor"
        verbose_name_plural = "Asesores"
    
    def save(self, *args, **kwargs):
        if self.codigo_asesor:
            self.codigo_asesor = self.codigo_asesor.upper()
        if self.nombre_completo:
            self.nombre_completo = self.nombre_completo.upper()
        if self.correo_electronico:
            self.correo_electronico = self.correo_electronico.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre_completo

# ====================================================================
# 3. Evaluador
# ====================================================================

class Evaluador(models.Model):
    """Modelo para el personal encargado de evaluar el proyecto."""
    codigo_evaluador = models.CharField(max_length=20, primary_key=True, verbose_name="CÓDIGO DE EVALUADOR")
    nombre_completo = models.CharField(max_length=200, verbose_name="NOMBRE COMPLETO")
    correo_evaluador = models.EmailField(verbose_name="CORREO EVALUADOR")
    especializacion = models.CharField(max_length=100, verbose_name="ESPECIALIZACIÓN")
    
    class Meta:
        verbose_name = "Evaluador"
        verbose_name_plural = "Evaluadores"

    def save(self, *args, **kwargs):
        if self.codigo_evaluador:
            self.codigo_evaluador = self.codigo_evaluador.upper()
        if self.nombre_completo:
            self.nombre_completo = self.nombre_completo.upper()
        if self.correo_evaluador:
            self.correo_evaluador = self.correo_evaluador.upper()
        if self.especializacion:
            self.especializacion = self.especializacion.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre_completo
