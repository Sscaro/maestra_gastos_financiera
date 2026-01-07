'''
Modulo con funciones auxiliares.
'''
import numpy as np
import pandas as pd
import yaml
from loguru import logger
import time
import os
import ast
from functools import reduce
import operator

def medir_tiempo(func):
    
    def wrapper(*args, **kwargs):
        inicio = time.time()
        resultado = func(*args, **kwargs)
        fin = time.time()
        print(f"⏱ Tiempo lectura archivo '{func.__name__}': {fin - inicio:.3f} segundos")
        return resultado
    return wrapper


def cargar_archivo_yml(archivo_config):
    """
    funcion para cargar archivo de configuación usuario
    arg: archivo_config: str
    return: dict
    """
    try:
        with open(archivo_config, 'r',encoding='utf-8') as file:
            configuracion = yaml.safe_load(file)
        return configuracion
    except Exception as e:
        logger.critical(f"Proceso de lectura de configuración fallido {e}  Revisa que el archivo exista")
        raise e


@medir_tiempo
def leer_excel(ruta,
               titulos= None,
               borrar_filas= None,
               nombre_hoja='Sheet1',
               col_usar=None,
               tipo_datos=None):
    """
    Lee un archivo Excel SAP Analysis for Office.
    Elimina la primera fila, y normaliza columnas.
    return df (pl.DataFrame): DataFrame con los datos del Excel.
    """
    
    df = pd.read_excel(
        ruta,
        sheet_name=nombre_hoja,
        skiprows = borrar_filas,
        names = titulos,
        usecols= col_usar,
        dtype= tipo_datos,
        engine='openpyxl'
    )
    return df

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

def agrupar_dataframe(   
    df: pd.DataFrame,
    vars_categoricas: list,
    vars_numericas_ops: dict
    ):
    '''
    Agrupa un DataFrame según las variables categóricas y aplica operaciones
    '''
    df_agrupado = (
        df
        .groupby(vars_categoricas, as_index=False, dropna=False)
        .agg(vars_numericas_ops)
    )
    return df_agrupado

def realizar_merge(df_left, 
                   df_right,
                   left_on,
                   right_on,
                   como='left',
                   sufijos="('_left','_right')"):
    '''
    documentacion for realizar_merge
    
        param df_left: data frame principal
        param df_right: data frame secundario
        param left_on: union data frame principal
        param right_on: union data frame secundario
        param how: tipo de union
        return: data frame unido
   
    '''

    data_unidad = pd.merge(df_left, 
                           df_right, 
                           left_on=left_on, 
                           right_on=right_on, 
                           how= como,
                           suffixes=ast.literal_eval(sufijos))
    return data_unidad

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

def reemplazo_valores(df:pd.DataFrame, reemplazo, colcondicion, colreemplazo):
    '''
    Funcion que permite a partir de un diccionario cambiar los valores segun el usuario indique
    ARG: df: data frame
    reemplazo: diccionario clave: condición, valor: reemplazo
    colcondicion = columna que quiere condicionar
    colreemplazo = columna que quiere se le aplique el cambio
    '''
    for condincion, nuevovalor in reemplazo.items():
        df_filtro = df[df[colcondicion]==condincion]
        df.loc[df_filtro.index, colreemplazo] = nuevovalor
    
    return df


def aplicar_condiciones(df, configuracion):
    """
    Funcion que a partir de un archivo de configuración realiza cambios
    que el usuario ha parametrizado. 
    """    
    
    for regla in configuracion:
        try:
            condiciones = [df[cond['columna']] == cond['valor'] 
                           for cond in regla['columnas_condicion']]
            condicion_total = condiciones[0]
            for condicion in condiciones[1:]:
                condicion_total &= condicion  # AND lógico entre las condiciones
            # Aplicar el reemplazo solo donde se cumplan todas las condiciones
            df.loc[condicion_total, regla['columna_reemplazo']] = regla['valor_reemplazo']
        

        except KeyError as e:
            logger.warning(
                f"La columna {e} no pudo ser filtrada porque no se encuentra en el DataFrame ⚠️"
            )
        
    return df


def insertar_valor_lista(lista, valor, posicion):
    nueva_lista = lista.copy()
    if posicion < 0:
        posicion = 0
    elif posicion > len(nueva_lista):
        posicion = len(nueva_lista)
    nueva_lista.insert(posicion, valor)
    return nueva_lista

def concatenar_df(df_completo, df_nuevo):
    columnas_df_completo = set(df_completo.columns)
    columnas_df_nuevo = set(df_nuevo.columns)
    
    if columnas_df_nuevo.difference(columnas_df_completo):
        raise ValueError("Error: Con las columnas de Real ppto y agrupaciones, corrige e intenta de nuevo ❌")
    else:
        df_resultado = pd.concat([df_completo,df_nuevo],axis=0)
        return df_resultado

class formato_textos:
    '''
    Clase para formatear textos en columnas de DataFrame de manera estatica (no se necesita instaniar la clase)
    como si fuese una libreria de formateo de textos.
    '''

    @staticmethod
    def capitalize(column):
        return column.astype(str).str.capitalize()

    @staticmethod
    def title(column):
        return column.astype(str).str.title()

    @staticmethod
    def upper(column):
        return column.astype(str).str.upper()
    
class filtrar_dataFrames:

    operadores = {
        "==": lambda s, v: s == v,
        "!=": lambda s, v: s != v,
        ">":  lambda s, v: s > v,
        ">=": lambda s, v: s >= v,
        "<":  lambda s, v: s < v,
        "<=": lambda s, v: s <= v,
        "in": lambda s, v: s.isin(v),
        "not in": lambda s, v: ~s.isin(v),
    }
    operado_logico = { 
        "and": operator.and_,
        "or": operator.or_
        }       

    @staticmethod
    def filtrar(df:pd.DataFrame, filtros:dict, logica="and"):
        
        masks = []
        col = filtros.get("columna")
        op = filtros.get("operador")
        valor = filtros.get("valor")
        if col not in df.columns:
            raise KeyError(f"Columna '{col}' no existe")    
        mask = filtrar_dataFrames.operadores[op](df[col], valor)
        masks.append(mask)

        final_mask = reduce(filtrar_dataFrames.operado_logico[logica], masks)
        return df.loc[final_mask]
    
