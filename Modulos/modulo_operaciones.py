from loguru import logger
from .assert_ppto import validacion_calidad
from helpers import agrupar_dataframe, realizar_merge, cargar_archivo_yml
from helpers import realizar_merge, aplicar_condiciones,concatenar_df
from helpers import filtrar_dataFrames, formato_textos
from .ajustes_archivos import ajustes_archivos_gasto
from pandas import to_datetime 

def funcion_inconsistecias(objeto_agrupaciones,config,path_real_ppto ):
    logger.info("Este paso solo evaluara si el archivo real ppto tiene inconsistencias con mayusulas o minusculas al finalizar deberás nuvamente lanzar el código..")
    data_real_ppto = objeto_agrupaciones.lectura_archivos({'ruta':path_real_ppto} | config['parametros_lectura_archivos']['libro_real_ppto'])
    bol=  validacion_calidad(data_real_ppto, config['armar_driver'])
    return bol

def funcion_validacion_agrupa_distribucion(objeto_agrupaciones,config, rutaArchivoagrupa, rutaArchivodisitribucion ,dict_arch_param_agrupaciones, mes ):
    logger.info("Este paso evalua si hay concordancia entre ambos archivos AFO..")

    data_agrupaciones = objeto_agrupaciones.lectura_archivos_gastos(ruta_agrupaciones=rutaArchivoagrupa, 
                                                                    dict_param=dict_arch_param_agrupaciones,
                                                                    tipo_gasto=  config['col_archi_agrupa_mes'])
    #filtro Archivo agrupaciones segun configuracion
    for filtro in config['filtros_archi_agrupaciones']:
        data_agrupaciones = filtrar_dataFrames.filtrar(data_agrupaciones, filtro)
    dict_arch_param_distribucion= config['parametros_lectura_archivos']['libro_distribucion']
    data_distribucion = objeto_agrupaciones.lectura_archivos_gastos(ruta_agrupaciones=rutaArchivodisitribucion,
                                                                    dict_param=dict_arch_param_distribucion,
                                                                    tipo_gasto=config['col_archivo_distrb_mes'])
    
    data_agrupaciones = agrupar_dataframe(data_agrupaciones,
                                                 config['validacion_agrupaciones']['columnas_agrupaciones'],
                                                 {mes:'sum'})
    data_distribucion = agrupar_dataframe(data_distribucion,
                                                 config['validacion_agrupaciones']['coluumnas_distribucion'],
                                                 {mes:'sum'})
    parametros_merge = {'df_left':  data_agrupaciones,
                        'df_right': data_distribucion} | config['uniones_merge']
    data_para_validar = realizar_merge(**parametros_merge)
    data_para_validar['diferencia'] = data_para_validar.iloc[:, -1] - data_para_validar.iloc[:, -2]   
    
    return data_para_validar

def ajuste_agrupaciones(objeto_agrupaciones, config,path_real_ppto,rutaArchivoagrupa,dict_arch_param_agrupaciones,
                        path_config_reemplazos , mes):
    '''
    Docstring for ajuste_agrupaciones    
    Funcion para realizar ajustes en el archivo de Agrupaciones
    Los parametros corresponden a rutas de archivos, diccionarios de configuración y el objeto para realizar calculos.
    devuelve: Data Frame con los ajustes y las columnas ordenadas para su revisión
    '''

    
    logger.info("Este paso realizará los respectivos calculos y ajustes del archivo agrupaciones")
    data_real_ppto = objeto_agrupaciones.lectura_archivos({'ruta':path_real_ppto} | config['parametros_lectura_archivos']['libro_real_ppto'] |
                                                          {'tipo_datos': str})
    for col, metodo in config['columnas_ppto_real'].items():
        data_real_ppto[col] = getattr(formato_textos,metodo)(data_real_ppto[col])
    
    #leyendo archivo
    data_agrupaciones = objeto_agrupaciones.lectura_archivos_gastos(ruta_agrupaciones=rutaArchivoagrupa,
                                                                dict_param=dict_arch_param_agrupaciones,
                                                                tipo_gasto=  config['col_archi_agrupa_mes'])
    
    # realizando filtros según configuración
    for filtro in config['filtros_archi_agrupaciones']:
        data_agrupaciones = filtrar_dataFrames.filtrar(data_agrupaciones, filtro)
    # reemplazos segun archivo configuración
    config_reemlazos = cargar_archivo_yml(path_config_reemplazos)
    data_agrupaciones = aplicar_condiciones(data_agrupaciones,config_reemlazos['reemplazos'])
    # realizar driver a partir de archivo real ppto   
    for columnas, agrupaciones in config['armar_driver'].items():
        driver_ppto = ajustes_archivos_gasto.driver_real_ppto(data_real_ppto,
                                                             columnas,
                                                             agrupaciones)
        diccionario_merge = {'df_left': data_agrupaciones,'df_right': driver_ppto,
                              'left_on': columnas, 'right_on': columnas}
        data_agrupaciones = realizar_merge(**diccionario_merge)
       #Creando archivo de Agrupaciones para su revisión
    # orden de las columnas para archivo de agrupaciones
    columnas_ordenadas = [k for k, v in config['listado_columnas_agrupado'].items() if v == "mantener"]
    columnas_ordenadas.append(mes) # se añade el mes al final
    data_agrupaciones = data_agrupaciones[columnas_ordenadas]
    return data_agrupaciones

def funcion_anexar_real_ppto(objeto_agrupaciones,config, path_real_agrupaciones, path_real_ppto,mes):

    logger.info("Se inicia cargando archivo de agrupaciones con ajustes hechos por usuario ℹ️")
 
    columnas_anexar_agrupaciones = [k for k, v in config['listado_columnas_agrupado'].items() if v == "anexar"]
    data_agrupaciones = objeto_agrupaciones.lectura_archivos({'ruta':path_real_agrupaciones} | {'tipo_datos':str})
    # anexando nuevas columnas
    for nueva_col in columnas_anexar_agrupaciones:
        if nueva_col == 'Año':
            data_agrupaciones[nueva_col] = config['Año'][1]
        else:
            data_agrupaciones[nueva_col] = "-"
    
    lista_meses_anexar = [meses_lista for meses_lista in config['listameses'] if meses_lista != mes]
   
    for nuevos_meses in lista_meses_anexar:
        data_agrupaciones[nuevos_meses] = 0
    data_real_ppto = objeto_agrupaciones.lectura_archivos({'ruta':path_real_ppto} | config['parametros_lectura_archivos']['libro_real_ppto'] |
                                                      {'tipo_datos': str})
    data_real_ppto[mes] = to_datetime(data_real_ppto[mes], errors="coerce").astype("float64")
    
    for mes_lista in config['listameses']:
        data_real_ppto[mes_lista] = to_datetime(data_real_ppto[mes_lista], errors="coerce").astype("float64")
    
    # Crea una copia del Real ppto del mes anterior antes de modificar
    logger.info("Se ha creado copia del archivo Real Ppto del mes anaterior en la carpeta salidas ℹ️")
    data_real_ppto.to_excel(r"Salidas\Real_Ppto_mes_anterior.xlsx",index=False)
        
    real_ppto_actualizado = concatenar_df(data_real_ppto,data_agrupaciones )
    diccionario_meses_operacion = {mes: "sum" for mes in config['listameses']}
    
    real_ppto_actualizado = agrupar_dataframe(real_ppto_actualizado,
                                              list(config['columnas_ppto_real'].keys()),
                                              diccionario_meses_operacion)
    columnas_a_sumar = config['listameses'][:config['listameses'].index(mes) + 1]
    real_ppto_actualizado['Acumulado'] = real_ppto_actualizado[columnas_a_sumar].sum(axis=1)
    real_ppto_actualizado['Total'] = real_ppto_actualizado[config['listameses']].sum(axis=1)

    return real_ppto_actualizado