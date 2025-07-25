'''
Modulo para realizar validaciones iniciales de la plantilla real ppto.
'''

from loguru import logger
def validacion_calidad(data, diction):
    for nombre_col, valores in diction.items():
        for valor in valores:
            if valor != nombre_col:
                validar_unicidad_codigo_nombre(data, nombre_col,valor)
    logger.info(f"No se encontraron más inconsistencias")
# Función para validar consistencia de mapeos uno a uno
def validar_unicidad_codigo_nombre(df, codigo_col, nombre_col):
    inconsistencias = (
        df[[codigo_col, nombre_col]]
        .drop_duplicates()
        .groupby(codigo_col)[nombre_col]
        .nunique()
    )
    inconsistencias = inconsistencias[inconsistencias > 1]
    if not inconsistencias.empty:
        logger.info(f"Inconsistencias encontradas para {codigo_col} y {nombre_col}:")
        for cod in inconsistencias.index:
            nombres = df[df[codigo_col] == cod][nombre_col].dropna().unique()
            logger.info(f"  {codigo_col}: {cod} → {nombre_col} encontrados: {list(nombres)}")
    #else:
    #    logger.info(f"No se encontraron inconsistencias para {codigo_col} y {nombre_col}.\n")
#Validar cada par
#validar_unicidad_codigo_nombre(data, "Nro Ceco", "Descripción Centro de Costos")
