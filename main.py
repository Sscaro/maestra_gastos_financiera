import os
import sys

from loguru import logger
from helpers.utils import Procesar_configuracion
import datetime as datetime
import tkinter as tk
import datetime as datetime
from tkinter import filedialog
import Modulos.validacion as vl
import Modulos.ajustesbases as aj
import Modulos.correcciones_real_ppto as ppto
from Modulos.assert_ppto import validacion_calidad
from Modulos.generar_drivers import generar_driver

root = tk.Tk()
root.withdraw()
config = Procesar_configuracion('Insumos/configcecos.yml')
reemplazos = Procesar_configuracion('Insumos/reemplazos.yml')

def run():

    listameses = config['listameses']
    logger.info("Comienza proceso \n sigue paso a paso las intrucciones...")

    mes1 = str(datetime.datetime.now().month)
    dia = str(datetime.datetime.now().day)
    hora = str(datetime.datetime.now().hour)
    Fecha = '{}_de_{}_hora_{}'.format(dia,mes1,hora)

    mes = input("Ingresa el nombre del mes que estas calculando\n")

    if mes.capitalize() not in listameses:
        print("Error, No ingresaste un nombre mes valido, ejecuta nuevamente")
        sys.exit()
    archivoagrupadistrimes = filedialog.askopenfilename(title="ingresa el del archivo de agrupación mes",
                                       filetypes=[("Archivos Excel", "*.xlsx;*.xls")])
    
    archivodistribcionmes = filedialog.askopenfilename(title="Ingresa el nombre del archivo distibución mes",
                                       filetypes=[("Archivos Excel", "*.xlsx;*.xls")])

    logger.info("Comencemos... \n por favor espera...")
    rutaArchivoagrupa = os.path.join(os.getcwd(),'Insumos',archivoagrupadistrimes)
    rutaArchivomes = os.path.join(os.getcwd(),'Insumos',archivodistribcionmes)
    ruta_realppto = os.path.join(os.getcwd(),'Insumos','Real_Ppto.xlsx')

    #respuesta = aj.moverarchivo(realppto)

    respuesta = False
    if respuesta:
        logger.info("Archivo de ppto guardado exitosamente en historico")
    else:
        logger.info("Archivo de ppto NO quedo en historico")

   
    acciones = ["0. Evaluar archivo Real Ppto" ,"1. Validación Afos", '2. Ajustes Base Agrupaciones','3. Generación Agrupaciones','4. Generar drivers']
    bol = True
    tablavedad = {'SI':True, 'NO':False, 'S':True, 'N':False}
    # DICCIONARIO PARA CAMBIAR ALGUNOS CECOS QUE SALEN COMO 99
    cambioCeco_tipo_gasto = config['Configurar_cecos_tipo_gastos']
    cambioCeco_tipo_centro= config['Configurar_cecos_tipo_centro']
    realppto  = ppto.ajustes_real_ppto(ruta_realppto,config['lista_columas_tipado'])

    logger.info("Se ha realizado copia de Real_ppto en la carpeta historico.")
    while bol == True:
        valor = int(input("ingresa el valor de 0 a 4 de las siguientes aciones: \n {} \n {} \n {} \n {} \n {} \n".format(acciones[0],acciones[1],acciones[2],acciones[3],acciones[4])))
        if valor == 0:
            logger.info("Este paso solo evaluara si el archivo real ppto tiene inconsistencias con mayusulas o minusculas al finalizar deberás nuvamente lanzar el codigo..")  
            validacion_calidad(realppto, config['armar_driver']) 
            bol = False      
        else:        
            if valor == 1:              
                logger.info("Por favor sigue las instrucciones..")          
                ejecucion = vl.validaciongastos(rutaArchivoagrupa,rutaArchivomes,mes,cambioCeco_tipo_gasto,cambioCeco_tipo_centro)  
                solucion = ejecucion.validacionCecos()   
                nombre_archivo = f"validacion{Fecha}.xlsx"
                solucion.to_excel("Salidas/"+nombre_archivo,index=False)
                logger.info("Validación exportada adecuantamente revisa carpeta salidas.")
                valor = input("Deseas continuar con alguna otra acción \n Digita 'SI  en caso contrario 'NO' \n ").upper()
                if valor in tablavedad.keys():
                    bol =tablavedad[valor]
                else:
                    bol = False           
            elif valor==2:
                logger.info("Comienza lectura archivo Real_Ppto para realizar ajustes de mayusculas y minusculas.")
                ejecucion = aj.ajustdistriagrupacion(realppto,rutaArchivoagrupa,mes.capitalize(),cambioCeco_tipo_gasto,cambioCeco_tipo_centro,reemplazos,config['armar_driver']) 
                        
                logger.info("Se ha copiado historico de Real_ppto Carpeta historicos.")
                logger.info("seguimos con los ajustes de la distribucion por agrupaciones.")
                baseajusagrupacion = ejecucion.organizarbase(config['lista_columas_tipado'])
                baseajusagrupacion.to_excel('Salidas/AjustesAgrupaciones.xlsx',index=False)
                logger.info("Proceso de ajustes listo revisar carpeta salidas.")
                valor = input("Deseas continuar con alguna otra acción \n Digita 'SI  en caso contrario 'NO' \n ").upper()
                if valor in tablavedad.keys():
                    bol =tablavedad[valor]
                else:
                    bol = False
                
            elif valor==3:
                ajustes = os.path.isfile(os.path.join(os.getcwd(),'Salidas','AjustesAgrupaciones.xlsx'))
                if ajustes:
                    rutaagrupaciones = os.path.join(os.getcwd(),'Salidas','AjustesAgrupaciones.xlsx')
                    concatenar = aj.anexobase(realppto,rutaagrupaciones,listameses,mes)
                    archivofinal = concatenar.anexarinfo()
                    archivofinal.to_excel('Insumos/Real_Ppto.xlsx',index=False)
                    logger.info("Se actualizó base de Real_ppto como insumos.")
                    archivofinal.to_excel('Salidas/Real_Ppto_{x}.xlsx'.format(x=mes),index=False)
                    archivofinal.to_excel('Insumos/Real_Ppto.xlsx',index=False)
                    logger.info("Archivo actualizado a mes {} se encuentra en carpeta salidas.".format(mes))
                    bol = False
                else:
                    logger.info("lo siento aun no has ejecutado el paso  'Ajustes Base Agrupaciones' \n por favor ejecuta nuevamente el paso 2 para poder ejecutar este paso.")
                    bol = False
            elif valor==4:
                driver =  generar_driver(ruta_realppto, config['armar_driver'], config['ajustes_driver'] )
                driver.generar_driver()
                logger.info("Se genero driver.")
   
    logger.info("Se termina el proceso.")

if __name__ == '__main__':
    run()
