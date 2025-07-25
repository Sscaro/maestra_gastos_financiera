import pandas as pd
from helpers.utils import Registro_tiempo
from datetime import datetime, timedelta
import os
import yaml
import unicodedata

def moverarchivo(base:pd.DataFrame): # metodo para copiar historico de ppto_real
        '''
        Crea un copia en foramto xlsx en una ruta historica
        '''
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        basehistorica = f"{fecha_actual}_{'Real_ppto.xlsx'}"
        rutadestino = os.path.join(os.getcwd(),'Historicos',basehistorica)
        base.to_excel(rutadestino,index=False)     
        return True



def reemplazo_valores(df, reemplazo, colcondicion, colreemplazo):
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
## funciones
def drivers(df,gastos,col1): 
    '''
    funcion que utiliza la misma maestra de gastos para extaer los nombres de los codigo
    de los diferente campos como concpeto, sub concepto , regional etc.
        ARGS
        df: Data frame con los gasots nuevos
        gastos: maestra de gastos anterior.
        col1: Columna que se quiere extraer los correspondientes nombres.
    '''
    df = df.drop_duplicates(keep='first')
    df = df.astype(str)
    #df = df.applymap(lambda x: str(x).title())
    gastos = pd.merge(gastos,df,on=col1, how= 'left')
    gastos = gastos.fillna("Vacio")
    return gastos

def dfarchivoAFO(ruta,n,nombrecol):#fucion para leer archivo con AFO
      gasto = pd.ExcelFile(ruta)
      gasto = gasto.parse('Hoja1',dtype=str)   
      gasto.columns = nombrecol     
      gasto = gasto[n:]
      gasto = gasto.reset_index(drop=True)
      gasto = gasto.drop(gasto.index[-1])
      A=gasto.columns[-2] 
      gasto[A]=gasto[A].astype(float)
      
      return gasto

def clean_column(column):
    """
    Limpia una columna de un DataFrame, eliminando tildes, caracteres especiales,
    convirtiendo a minúsculas y eliminando espacios en los extremos.
    """
    cleaned_column = column.apply(lambda x: unicodedata.normalize('NFKD', str(x)).encode('ascii', 'ignore').decode('utf-8'))
    cleaned_column = cleaned_column.str.capitalize().str.strip()
    return cleaned_column

def cargar_configuracion(archivo_config):
    """
    funcion para cargar archivo de configuación usuario
    """
    with open(archivo_config, 'r',encoding='utf-8') as file:
        configuracion = yaml.safe_load(file)
    return configuracion

def aplicar_configuracion(df, configuracion):
    """
    Funcion que a partir de un archivo de configuración realiza cambios
    que el usuario ha parametrizado. 
    """    
    
    for regla in configuracion:
        condiciones = [df[cond['columna']] == cond['valor'] for cond in regla['columnas_condicion']]
        condicion_total = condiciones[0]
        for condicion in condiciones[1:]:
            condicion_total &= condicion  # AND lógico entre las condiciones
        # Aplicar el reemplazo solo donde se cumplan todas las condiciones
        df.loc[condicion_total, regla['columna_reemplazo']] = regla['valor_reemplazo']
    
    return df

def capitalize_column(column):
    """
    funcion para poner la primera letra en mayuscula en una cadena de caracteres    
    """
    return column.apply(lambda x: x.capitalize())

def title_column(column):
    """
    funcion para poner la primera letra en mayusculas despues de un espacio  
    """
    return column.apply(lambda x: x.title())
def upper_column(column):
    """
    funcion para poner todas las letras en mayusuculas en una cadena de caracteres 
    """
    return column.apply(lambda x: x.upper())

### CLASE
class ajustdistriagrupacion:

    '''
    Clase para realizar diferentes cruces con base en el archivo consolidado para el mes nuevo.
    '''
    def __init__(self,base,Gastos_Sin_Dist_Mes_Agrupaciones,mes,cecos,tipo_centro,reemplazos_yml,configdriver) -> None:
        self.base = base # real y ppto en el archivo historico del gasto
        self.agruapa = Gastos_Sin_Dist_Mes_Agrupaciones # consulta de sin distribucion y con agrupaciones.
        self.mes = mes # mes del cierre en formato mmm       
        self.cecos = cecos # cecos con 99 en tipo de gasto
        self.tipo_centro = tipo_centro # ceco con 99 en tipo de centro
        self.reemplazos_yml = reemplazos_yml
        self.configdriver = configdriver
    
    @Registro_tiempo
    def organizarbase(self, dictionario:dict):
        data = self.base
        data.loc[:,'Enero':]=data.loc[:,'Enero':].astype(float)
        # aplciando transformación para las columnas del historico del gasto
        # columnas =  data.loc[:,:'Responsable'].columns
        #for i in columnas:
        #    data[i] = clean_column(data[i])

        nomcol = ['Clasificación Regionales','Detalle Clasif Regionales',
               'Tipo de gasto','Nro Ceco',
               'col1','Nro Cpto','col2','Nro Sub','col3',
               'POOL','col4','Of Ventas','col5',
               'col6','Cód Canal','col7','col8','Cód Cliente','col9',
               'Tipo','Col10','col11','Cuenta Contable',
               'col12', self.mes,'col13']
        
        parametro = dfarchivoAFO(self.agruapa,2,nomcol)
        parametro = self._OrganizaGastos(parametro)  

        for col, values in self.configdriver.items(): # ciclo que permite aramar drivers: col: columna a con valor clave, values, columnas resultantes
            parametro = drivers(data[values], parametro, col)

        #ordencol = ['Clasificación Regionales','','','']
        

        columnasUpper = dictionario['columnasUpper']
        columnascapitalize = dictionario['capitalize']
        columnnastitle = dictionario['columnnastitle']
        
 
        
        orden = ['Clasificación Regionales','Detalle Clasif Regionales','Tipo de gasto','Año','Nro Ceco','Descripción Centro de Costos',
                 'Nro Cpto','Descripción Concepto','Nro Sub','Descripción Subconcepto','POOL','POOL DE RECURSOS','Of Ventas',
                 'Descripción Of Ventas','Agrupa Regional','Cód Canal','Canal','Cód Linea-Marca','Cód Cliente','Tipo','Agrupa',
                 'Grupo Ceco','Agrupa Regional 2','Cuenta Contable','Descrip Cuenta','Responsable','Parametro','Gerencia','Observaciones','Clase',
                 'Agrupa Gerencia / Regional',self.mes]
        
        print(parametro.info())
        parametro['Observaciones']= '-'
        parametro['Clase']='-'  
        parametro[columnasUpper]=parametro[columnasUpper].apply(capitalize_column)
        parametro[columnascapitalize]=parametro[columnascapitalize].apply(capitalize_column)
        parametro[columnnastitle]=parametro[columnnastitle].apply(title_column)
        parametro = parametro[orden]
        
        return parametro

    def _OrganizaGastos(self,base):
        columnas_con_col = [columna for columna in base.columns if 'col' in columna] # LISTA PARA ELIMINAR DESCRIPCIONES ORIGINALES DEL AFO
        basefil = base.loc[:, ~base.columns.isin(columnas_con_col)]
        if len(self.cecos) > 0:
            basefil = reemplazo_valores(basefil, self.cecos,'Nro Ceco','Tipo de gasto')
            basefil = reemplazo_valores(basefil, self.tipo_centro,'Nro Ceco','Tipo')
        
        basefil = basefil[basefil['Tipo de gasto']!='99']
        
        año = datetime.now() - timedelta(days=30)
        basefil['Año']= 'Real {y}'.format(y=año.year)
                
        basefil = aplicar_configuracion(basefil, self.reemplazos_yml['reemplazos'])
      
        basefil['Cód Canal'] = basefil['Cód Canal'].replace('#','Sin Asignar')

        basefil.loc[(basefil['Clasificación Regionales']=='Nómina') & (basefil['Detalle Clasif Regionales']=='Nómina'),
                    'Nro Cpto']='10'
        basefil['Cód Linea-Marca']  = '(en blanco)'
        basefil['Responsable']  = '(en blanco)'
        basefil.loc[(basefil['Clasificación Regionales']=='Nómina') & 
                    (basefil['Detalle Clasif Regionales']=='Nómina'),
                    'Nro Sub']='100'
        ## aplicar la funcion para eliminar posibles inconsistencias den el tipado
        columnasrevisar = basefil.columns

        for i in columnasrevisar:
            if i != self.mes:
                basefil[i] = clean_column(basefil[i])
            else:
                pass

        return basefil

class anexobase: # clase para anexar agrupaciones a base acumulada.
    def __init__(self,baseppto, basegrupaciones,listameses,mes) :
        self.baseppto = baseppto
        self.baseagrupaciones = basegrupaciones
        self.listameses = listameses
        self.mes = mes.capitalize()

    @Registro_tiempo
    def anexarinfo(self):
        ppto = self.baseppto
        agrupaciones = pd.read_excel(self.baseagrupaciones,dtype=str)       
        ppto.loc[:,'Enero':'Diciembre']=ppto.loc[:,'Enero':'Diciembre'].astype(float)   
        A=agrupaciones.columns[-1]
        agrupaciones[A]=agrupaciones[A].astype(float)
        total = pd.concat([ppto,agrupaciones],axis=0)
        total.loc[:,'Enero':'Diciembre'] = total.loc[:,'Enero':'Diciembre'].fillna(0)

        agrupadores = list(total.loc[:,:'Agrupa Gerencia / Regional'].columns)
        sumas = list(total.loc[:,'Enero':'Diciembre'].columns)
        diccionario_suma  = {col: 'sum' for col in sumas}
        total = total.groupby(agrupadores,dropna=False).agg(diccionario_suma).reset_index()        
        columnas_a_sumar = self.listameses[:self.listameses.index(self.mes) + 1]
        total['Acumulado'] = total[columnas_a_sumar].sum(axis=1)
        total['Total'] = total[self.listameses].sum(axis=1)

        return total
    
# procedimientos de prueba


'''
rutadestino = os.path.join(os.getcwd(),'Insumos','Real_Ppto.xlsx')
agrupaciones = os.path.join(os.getcwd(),'Insumos','Gastos_Sin_Dist_Mes_Agrupaciones.xlsx')
ejecucion = ajustdistriagrupacion(rutadestino,agrupaciones,'Noviembre')
lista = ejecucion.organizarbase()
lista.to_excel('ejemplo.xlsx',index=False)
'''