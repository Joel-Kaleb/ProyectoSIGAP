import pandas as pd
import os
import logging
from django.db import transaction
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from datetime import date
from decouple import config

# Importar Modelos
from projects.models import Proyecto, Formato1, Participacion
from people.models import Alumno, Asesor


logger = logging.getLogger(__name__)

RUTA_PROCESADOS = config('RUTA_PROCESADOS')
NOMBRE_ARCHIVO_BASE = config('NOMBRE_ARCHIVO_BASE')

# --- Funciones Auxiliares ---
def is_admin(user):
    return user.is_superuser or user.is_staff

def get_clean_value(row, key):
    """
    Obtiene un valor, asegura que es una cadena y maneja valores nulos/NaN de Pandas 
    sin ambigüedad de Series.
    """
    value = row.get(key)
    
    # 1. Manejo de ambigüedad (si el valor es un array/Series) y de nulos
    if isinstance(value, pd.Series):
        # --- INICIO DE CORRECCIÓN ---
        # Si es una Serie (claves duplicadas), buscar el primer valor NO NULO
        found_value = None
        for v in value:
            # strip() para manejar strings con solo espacios en blanco
            if pd.notna(v) and (not isinstance(v, str) or v.strip() != ""):
                found_value = v
                break # Tomar el primer valor no nulo
        
        value = found_value # Ahora 'value' es un valor simple (o None)
        # --- FIN DE CORRECCIÓN ---
    
    if pd.isna(value) or value is None:
        return None
    
    try:
        # Intenta convertir a entero para eliminar decimales (si es código/float) y luego a string
        if isinstance(value, (int, float)):
            if value == 0 or value == 0.0:
                return None
            return str(int(value))
        return str(value).strip()
    except Exception:
        return str(value).strip() if value is not None else None

# --- Vista Principal ---
@user_passes_test(is_admin)
def importar_proyectos_view(request):
    context = {}
    
    fecha_actual = date.today()
    año_actual = str(fecha_actual.year)
    mes_actual = fecha_actual.month
    
    letra_semestre = "A" if mes_actual < 7 else "B"
    calendario_actual = año_actual + letra_semestre
    
    nombre_archivo_final = NOMBRE_ARCHIVO_BASE.replace('- ', f'-{calendario_actual} ')
    
    RUTA_COMPLETA = os.path.join(
        RUTA_PROCESADOS, 
        calendario_actual, 
        '1-Procesados', 
        nombre_archivo_final
    )
    
    if not os.path.exists(RUTA_COMPLETA):
        context['error'] = f"Error: No se encontró el archivo en la ruta: {RUTA_COMPLETA}."
        return render(request, 'importar_proyectos.html', context)
    
    if request.method == 'POST':
        try:
            df = pd.read_excel(RUTA_COMPLETA)
            registros_exitosos = 0
            registros_fallidos = 0
            
            # NORMALIZACIÓN
            df.columns = (
                df.columns.str.strip().str.lower()
                .str.replace('(', '', regex=False).str.replace(')', '', regex=False) # Eliminar paréntesis
                .str.replace('á', 'a').str.replace('é', 'e').str.replace('í', 'i').str.replace('ó', 'o').str.replace('ú', 'u')
                .str.replace('ñ', 'n')
                .str.replace(' ', '_') # Reemplazar espacios por guiones bajos (ÚLTIMO PASO)
            )
            
            # 1. Obtenemos una lista de claves de columna ÚNICAS, 
            #    pero manteniendo el orden.
            unique_keys = list(dict.fromkeys(df.columns))

            # 2. Creamos dinámicamente las listas de búsqueda
            #    basado en las columnas que *realmente* existen.
            
            # Buscará 'variante', 'variante.1', ... 'variante.N'
            DYNAMIC_VARIANTE_KEYS = [key for key in unique_keys if key.startswith('variante')]

            with transaction.atomic():
                for index, row in df.iterrows():
                    
                    # 1. IDENTIFICACIÓN CLAVE (REPRESENTANTE)
                    # CLAVE CORREGIDA: Buscamos la clave sin los paréntesis, que ahora fue simplificada a:
                    codigo_representante = get_clean_value(row, 'codigo_de_integrante_1representante')
                    
                    if not codigo_representante:
                        logger.warning(f"Fila {index + 2}: Salto - Código de representante vacío.")
                        registros_fallidos += 1
                        continue

                    folio_proyecto = f"{codigo_representante}-{calendario_actual}" 
                    
                    try:
                        # 2. PROCESAR ASESOR
                        nombre_asesor = get_clean_value(row, 'nombre_del_asesor')
                        correo_asesor = get_clean_value(row, 'correo_institucional_del_asesora')
                        
                        # --- INICIO DE CORRECCIÓN (Versión Definitiva) ---
                        
                        # Leemos la clave ÚNICA Y VERDADERA que viene del Excel
                        codigo_asesor_excel = get_clean_value(row, 'codigo_del_asesor')

                        # VALIDACIÓN: Esta es la clave principal, NO puede estar vacía
                        if not codigo_asesor_excel:
                            logger.warning(f"Fila {index + 2} (Folio: {folio_proyecto}): Salto - 'Codigo del asesor' está vacío. No se puede procesar.")
                            registros_fallidos += 1
                            continue # Saltar esta fila

                        # LÓGICA CORREGIDA: Usar el CÓDIGO DEL EXCEL como clave única
                        asesor_obj, _ = Asesor.objects.update_or_create(
                            codigo_asesor=codigo_asesor_excel,  # <-- CAMBIO: Clave única real
                            defaults={
                                'nombre_completo': nombre_asesor,
                                'correo_electronico': correo_asesor
                                # Ya no generamos ningún código hash, usamos el que viene del Excel
                            }
                        )

                        # 3. PROCESAR FORMATO1 
                        formato1_obj, _ = Formato1.objects.update_or_create(
                            folio=folio_proyecto,
                            defaults={
                                'introduccion': get_clean_value(row, 'introduccion'),
                                'justificacion': get_clean_value(row, 'justificacion'),
                                'objetivo': get_clean_value(row, 'objetivo'),
                                'resumen': get_clean_value(row, 'resumen'),
                            }
                        )
                        
                        # 4. BUSCAR LAS URLs DE FORMA SEPARADA

                        # --- LÓGICA PARA 'evidencia_url' (Principal) ---
                        # Tomamos el valor directamente de 'sube_tu_evidencia'
                        evidencia_url_principal = get_clean_value(row, 'sube_tu_evidencia')
                        # 4.5 BUSCAR LA VARIANTE (EN MÚLTIPLES COLUMNAS)
                        
                        valor_variante_encontrado = None
                        for col_name in DYNAMIC_VARIANTE_KEYS:
                            valor = get_clean_value(row, col_name)
                            if valor:
                                valor_variante_encontrado = valor
                                break

                        
                        # 5. CREAR/ACTUALIZAR PROYECTO (MAESTRO) - CORREGIDO
                        proyecto_obj, _ = Proyecto.objects.update_or_create(
                            folio=folio_proyecto,
                            defaults={
                                # Título y Modalidad
                                'titulo': get_clean_value(row, 'titulo_del_proyecto'),
                                'modalidad': get_clean_value(row, 'modalidad'),
                                
                                # Mapeo: Nivel y Variante
                                'nivel_competencia': get_clean_value(row, 'nivel_de_competencias'), # Módulos Registrados
                                'variante': valor_variante_encontrado,
                                
                                'calendario_registro': calendario_actual,
                                'asesor': asesor_obj,
                                'formato1': formato1_obj,
                                
                                # --- ASIGNACIÓN CORREGIDA ---
                                'evidencia_url': evidencia_url_principal,
                                'protocolo_dictamen_url': get_clean_value(row, 'sube_tu_formato'),
                            }
                        )
                        
                        # 6. PROCESAR INTEGRANTES Y PARTICIPACIÓN
                        integrantes_data = []
                        for i in range(1, 4):
                            
                            if i == 1:
                                # Integrante 1 (Representante) - Claves limpias
                                codigo_key = 'codigo_de_integrante_1representante'
                                nombre_key = 'nombre_de_integrante_1representante'
                                correo = get_clean_value(row, 'direccion_de_correo_electronico')
                            else:
                                # Integrantes 2 y 3 - Claves genéricas
                                codigo_key = f'codigo_de_integrante_{i}'
                                nombre_key = f'nombre_de_integrante_{i}'
                                correo = None

                            codigo = get_clean_value(row, codigo_key)
                            nombre = get_clean_value(row, nombre_key)
                            
                            if codigo and nombre:
                                integrantes_data.append({
                                    'codigo': codigo,
                                    'nombre': nombre,
                                    'es_representante': (i == 1),
                                    'correo': correo
                                })
                        
                        # 7. Guardar Alumnos y Participación
                        for data in integrantes_data:
                            alumno_obj, _ = Alumno.objects.update_or_create(
                                codigo_estudiante=data['codigo'],
                                defaults={
                                    'nombre_completo': data['nombre'],
                                    'correo_electronico': data['correo']
                                }
                            )
                            # Crear la relación de participación
                            Participacion.objects.update_or_create(
                                proyecto=proyecto_obj,
                                alumno=alumno_obj,
                                defaults={'es_representante': data['es_representante']}
                            )

                        registros_exitosos += 1

                    except Exception as e:
                        registros_fallidos += 1
                        logger.error(f"Fila {index + 2} (Folio: {folio_proyecto}): Fallo al guardar. Error: {e}")

            context['success_message'] = f"Importación completada. Registros exitosos: {registros_exitosos}. Fallidos: {registros_fallidos}."
        
        except Exception as e:
            context['error'] = f"Ocurrió un error inesperado durante la importación. Detalle: {e}"
            logger.exception("Error fatal en la importación de proyectos.")
            
    return render(request, 'importar_proyectos.html', context)