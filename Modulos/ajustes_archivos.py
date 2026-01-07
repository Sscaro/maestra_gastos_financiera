from helpers import utils

class ajustes_archivos_gasto:

    def __init__(self,config, mes):
        self.config = config # ruta del archivo de configuración
        self.mes = mes # mes a calcular      
        
    def lectura_archivos_gastos(self,ruta_agrupaciones , tipo_gasto ,dict_param={}):

        dict_manejo_col_agupaciones = tipo_gasto
        dict_manejo_col_agupaciones[self.mes] = dict_manejo_col_agupaciones.pop("mes")
    
        nombre_columnas = list(dict_manejo_col_agupaciones.keys())
        
        lista_col_incluir = [
                clave
                for clave, valores in dict_manejo_col_agupaciones.items()
                if valores[1] == "mantener"
                ]

        dict_tipado = {
                clave: valores[0]
                for clave, valores in dict_manejo_col_agupaciones.items()
                if valores[1] == "mantener"
                }
        
        diccionario = {"ruta": ruta_agrupaciones} | dict_param | {"titulos":nombre_columnas }|{"col_usar":lista_col_incluir} | {"tipo_datos":dict_tipado }
        data = self.lectura_archivos(diccionario)
        return data
    
    def lectura_archivos(self, diccionario_parametros):
        data = utils.leer_excel(**diccionario_parametros)
        return data
    
    @staticmethod
    def driver_real_ppto(df,col_clave, columas_dependientes):
        df = df[columas_dependientes]
        df = df.drop_duplicates(subset=[col_clave])
        return df
       
import pandas as pd

class generar_driver:
    '''
    Clase para calcular tablas con drivers
    '''
    def __init__(self, df_ppto:str, config: dict ):
        '''
        arg: df_ppto: Pd.DataFrame con la información del real ppto (archivo raiz)
        config: dict: con los valores a calcular drivers
        '''
        self.df_ppto = pd.read_excel(df_ppto,dtype=str)
        self.config = config
          
    def generar_driver(self):
        '''
        Realiza calculos corresponcientes        
        '''

        dict_data_frames = {}
        for col, values in self.config.items(): # ciclo que permite aramar drivers: col: columna a con valor clave, values, columnas resultantes
            values.append('Responsable')
            parametro = self.df_ppto[values]
            parametro = parametro.drop_duplicates(keep='first')
            dict_data_frames[col] = parametro

        #Agurpaciones_adicional

        df_driver = self.df_ppto[self.config['ajustes_driver']['driver_completo_columnas']]
        anio = self.config['Año']

        df_driver = df_driver[df_driver['Año'].isin(anio)]        
        df_driver = df_driver.drop_duplicates(keep='first')
        dict_data_frames['driver_completo'] = df_driver
        
        with pd.ExcelWriter('Salidas\drivers.xlsx', engine='openpyxl') as writer:
            for hoja, df in dict_data_frames.items():
                df.to_excel(writer, sheet_name=hoja, index=False)

        return True