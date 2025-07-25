'''
Modulo con funciones auxiliares.
'''

import numpy as np
import pandas as pd
import yaml
from loguru import logger
import time


def Registro_tiempo(original_func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = original_func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(
            f"Tiempo de ejecución de {original_func.__name__}: {execution_time} segundos"
        )
        return result

    return wrapper


def Procesar_configuracion(nom_archivo_configuracion: str) -> dict:
    """Lee un archivo YAML de configuración para un proyecto.

    Args:
        nom_archivo_configuracion (str): Nombre del archivo YAML que contiene
            la configuración del proyecto.

    Returns:
        dict: Un diccionario con la información de configuración leída del archivo YAML.
    """
    try:
        with open(nom_archivo_configuracion, "r", encoding="utf-8") as archivo:
            configuracion_yaml = yaml.safe_load(archivo)
        logger.success("Proceso de obtención de configuración satisfactorio")
    except Exception as e:
        logger.critical(f"Proceso de lectura de configuración fallido {e}")
        raise e

    return configuracion_yaml

def reducir_uso_memoria(df: pd.DataFrame) -> pd.DataFrame:
    '''
    Iterar sobre todas las columnas de un dataframe y modificar su tipo de dato para
    reducir el uso de memoria

    Args:
        DataFrame: Dataframe para ajustar los tipos de datos

    Returns:
        Dataframe: Un Dataframe de pandas con los tipos de datos ajustados
    '''

    # mem_inicial = df.memory_usage().sum() / 1024**2
    # print('El uso de memoria del dataframe es {:.2f} MB'.format(mem_inicial))

    for col in df.columns:
        tipo_dato_col = df[col].dtype

        if str(tipo_dato_col) != 'object':
            c_min = df[col].min()
            c_max = df[col].max()
            if str(tipo_dato_col)[:3] == 'int':
                if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                    df[col] = df[col].astype(np.int8)
                elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                    df[col] = df[col].astype(np.int16)
                elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                    df[col] = df[col].astype(np.int32)
                elif c_min > np.iinfo(np.int64).min and c_max < np.iinfo(np.int64).max:
                    df[col] = df[col].astype(np.int64)
            else:
                if c_min > np.finfo(np.float16).min and c_max < np.finfo(np.float16).max:
                    df[col] = df[col].astype(np.float16)
                elif c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                    df[col] = df[col].astype(np.float32)
                else:
                    df[col] = df[col].astype(np.float64)
        else:
            df[col] = df[col].astype('category')
    return df

def agrupar_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrupa un DataFrame utilizando todas las columnas categóricas como claves 
    y suma las columnas numéricas.
    
    Parámetros:
        df (pd.DataFrame): El DataFrame a agrupar.
    
    Retorna:
        pd.DataFrame: El DataFrame agrupado.
    """
    # Identificar columnas categóricas (tipo objeto)
    columnas_categoricas = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    # Agrupar por columnas categóricas y sumar columnas numéricas
    df_agrupado = df.groupby(columnas_categoricas, as_index=False).sum(numeric_only=True)
    
    return df_agrupado


def ajustes_clientes_num(df,col1, col2, valor:str="#"):
    '''
    funcion para ajustar los # en vendedores
    arg: df, 
        col1 = col con valor con valor en #. 
        col2 = con con valor con cual imputar
    return df
    '''
    # Crear un diccionario con el cod_cliente y su cod_vendedor real (que no sea '#')
    valor_real = df[df[col1] != valor].groupby(col2)[col1].first()
    df[col1] = df.apply(lambda row: valor_real[row[col2]]
                        if row[col1] == valor and row[col2] in valor_real
                        else row[col1], axis=1)
    return df