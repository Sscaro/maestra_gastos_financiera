'''
Modulo para realizar validaciones iniciales de la plantilla real ppto.
'''
from loguru import logger
import sys

def validacion_calidad(data, diction):
    '''
    Docstring for validacion_calidad
    
    :param data: df frame
    :param diction: diccionario con columnas a validar
    '''
    bol = True
    for nombre_col, valores in diction.items():
        for valor in valores:
            if valor != nombre_col:
                bol = validar_unicidad_codigo_nombre(data, nombre_col,valor)
    logger.info(f"No se encontraron más inconsistencias")
    if bol == True:
        logger.info("El archivo de Real_Ppto cumple con las validaciones de calidad ✅")
        return True
    else:
        return False

# Función para validar consistencia de mapeos uno a uno
def validar_unicidad_codigo_nombre(df, codigo_col, nombre_col):
    
    inconsistencias = (
        df[[codigo_col, nombre_col]]
        .drop_duplicates()
        .groupby(codigo_col)[nombre_col]
        .nunique()
    )
    bol = True
    inconsistencias = inconsistencias[inconsistencias > 1]
    if not inconsistencias.empty:
        logger.info(f"Inconsistencias encontradas para {codigo_col} y {nombre_col}:")
        for cod in inconsistencias.index:
            nombres = df[df[codigo_col] == cod][nombre_col].dropna().unique()
            logger.info(f"  {codigo_col}: {cod} → {nombre_col} encontrados: {list(nombres)}")
        logger.info(f"Por favor, corrige estas inconsistencias antes de continuar.")
        bol =  False
   
    return bol

