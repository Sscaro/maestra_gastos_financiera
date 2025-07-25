'''
Modulo para generar los drivers con base en el real ppto

'''
import pandas as pd

class generar_driver:
    '''
    Clase para calcular tablas con drivers
    '''
    def __init__(self, df_ppto:str, config: dict, config_ad:dict ):
        '''
        arg: df_ppto: Pd.DataFrame con la información del real ppto (archivo raiz)
        config: dict: con los valores a calcular drivers
        '''
        self.df_ppto = pd.read_excel(df_ppto,dtype=str)
        self.config = config
        self.config_ad = config_ad

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

        df_driver = self.df_ppto[self.config_ad['driver_completo_columnas']]
        anio = self.config_ad['Año']

        df_driver = df_driver[df_driver['Año'].isin(anio)]        
        df_driver = df_driver.drop_duplicates(keep='first')
        dict_data_frames['driver_completo'] = df_driver
        
        with pd.ExcelWriter('Salidas\drivers.xlsx', engine='openpyxl') as writer:
            for hoja, df in dict_data_frames.items():
                df.to_excel(writer, sheet_name=hoja, index=False)

        return True