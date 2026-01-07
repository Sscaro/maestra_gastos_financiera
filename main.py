
from pathlib import Path
import datetime as datetime
import tkinter as tk
import datetime as datetime
from tkinter import filedialog
from Modulos import funcion_inconsistecias
from Modulos import  ajuste_agrupaciones
from Modulos import  funcion_validacion_agrupa_distribucion, funcion_anexar_real_ppto
from config_path_routs import setup_logger
from loguru import logger
from config_path_routs import ConfigPathRoutes as cpr
from helpers import cargar_archivo_yml
from Modulos import ajustes_archivos_gasto
from Modulos import generar_driver

root = tk.Tk()
root.withdraw()
path_config = cpr.resolver_rutas("Insumos", "config.yml")
config = cargar_archivo_yml(path_config)

path_config_cecos = cpr.resolver_rutas(config['ruta_config_cecos'])
path_config_reemplazos = cpr.resolver_rutas(config['ruta_config_reemplazos'])
path_real_ppto = cpr.resolver_rutas(config['ruta_real_ppto'])

def seleccionar_tarea(valor):

    rutaArchivoagrupa = filedialog.askopenfilename(title="ingresa el del archivo de agrupación mes",
                                       filetypes=[("Archivos Excel", "*.xlsx;*.xls")])
    
    rutaArchivodisitribucion = filedialog.askopenfilename(title="ingresa el del archivo de distirbucion mes",
                                       filetypes=[("Archivos Excel", "*.xlsx;*.xls")])
    
    listameses = config['listameses']
    mes = input("Ingresa el nombre del mes que estas calculando\n").capitalize()
    if mes not in listameses:
        raise ValueError('El mes ingresado no es valido')
    
    objeto_agrupaciones = ajustes_archivos_gasto(config, mes)
    
    dict_arch_param_agrupaciones= config['parametros_lectura_archivos']['libro_agrupaciones']
       
    if valor == 1:
        # validacion de archivo real_ppto (valida que no hayan valores repetidos)
        funcion_inconsistecias(objeto_agrupaciones, 
                                config,
                                path_real_ppto)
            
    elif valor == 2:
        # compara tanto el libro de agrupaciones como el libro de distribucion
        file = funcion_validacion_agrupa_distribucion(objeto_agrupaciones,
                                               config,
                                                rutaArchivoagrupa,
                                                rutaArchivodisitribucion,
                                                dict_arch_param_agrupaciones, 
                                                mes )
        file.to_excel(r'Salidas\Validaciones.xlsx',index=False)
                    
    elif valor == 3:
        df_agrupaciones_ajustado = ajuste_agrupaciones(objeto_agrupaciones,
                                                       config,
                                                       path_real_ppto,
                                                       rutaArchivoagrupa,
                                                       dict_arch_param_agrupaciones,
                                                       path_config_reemplazos, 
                                                       mes)      
        df_agrupaciones_ajustado.to_excel(r'Salidas\Agrupaciones.xlsx',index=False)

    elif valor == 4:
        # anexa información el archivo real ppto
        logger.info("Se inicia cargando archivo de agrupaciones con ajustes hechos por usuario ℹ️")
        path_real_agrupaciones = cpr.resolver_rutas(config['ruta_config_agrupaciones'])
        if not Path(path_real_agrupaciones).exists(): # evalua si archivo agrupaciones existe           
            raise FileNotFoundError(f"El archivo no existe: {path_real_agrupaciones.resolve()}")
        real_ppto = funcion_anexar_real_ppto(objeto_agrupaciones,
                                            config, 
                                            path_real_agrupaciones,
                                            path_real_ppto,
                                            mes)
        
        real_ppto.to_excel(r'Salidas\real_ppto_{}.xlsx'.format(mes),index=False)
        real_ppto.to_excel(r'Insumos\real_ppto.xlsx',index=False)
        logger.info("Finaliza exitosamente creación de real ppto mes {} ℹ️ el archivo esta en lla carpeta Salidas ".format(mes))


    elif valor == 5:
        driver =  generar_driver(path_real_ppto, config)
        driver.generar_driver()
        logger.info("Se genero driver.")
        return False
    else:
        raise ValueError("Opción no válida. Por favor, selecciona una opción del 1 al 5.")
    
    logger.info("Proceso terminado ✅.. \n ¿Deseas continuar con alguna otra acción?")
    
def run():
    
    logger.info("Comienza proceso \n sigue paso a paso las intrucciones...")

    ## logica para seleccionar tarea
    acciones = config['seleccion_tarea']
    

    logger.info("A contunacion lee las opciones a ejecutar: ℹ️: ")
    print("\n".join(f"{k}: {v}" for k, v in acciones.items()))        
    seleccion = int(input(f"ingresa el número de la acción a realizar: ℹ️ \n"))    
    seleccionar_tarea(seleccion)

if __name__ == '__main__':
    setup_logger()
    run()
