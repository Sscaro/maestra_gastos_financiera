'''
Modulo para organziar archivo real ppto
'''
import pandas as pd
from Modulos.ajustesbases import moverarchivo
def ajustes_real_ppto(ruta:str, lista_col:dict) -> pd.DataFrame :
    '''
    funcion para organizar las mayusculas y minusculas del archivo de ppto
    ARG: ruta: str ruta del archivo de excel
        lista_col: listado de las columnas a organizar
    RETURN: df: data frame organizado    '''

    df = pd.read_excel(ruta,dtype=str)
    #print(df.info())  
    for  funcion, lista in lista_col.items():
        if funcion == 'capitalize':
            for col in lista:
                if col in df.columns:
                    df[col] = df[col].astype(str).str.capitalize()
        if funcion == 'columnasUpper':
            for col in lista:
                if col in df.columns:
                    df[col] = df[col].astype(str).str.upper() 
        if funcion == 'columnnastitle':
            for col in lista:
                if col in df.columns:
                    df[col] = df[col].astype(str).str.title()  
    
    return df