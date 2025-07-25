'''
Modulo para validacion gastos distribucion agrupacion vs gastos SIN agrupacion
'''
import pandas as pd
from Modulos.ajustesbases import reemplazo_valores


def dfarchivoAFO(ruta,n,nombrecol):#fucion para leer archivo con AFO
      gasto = pd.ExcelFile(ruta)
      gasto = gasto.parse('Hoja1')
      gasto.columns = nombrecol
      gasto = gasto[n:]
      gasto = gasto.reset_index(drop=True)
      gasto = gasto.drop(gasto.index[-1])
      return gasto

class validaciongastos:
    def __init__(self,disagrupmes,dismes,mes,cambiocecos,cambio_centro):
        
        self.disagrupmes = disagrupmes
        self.dismes = dismes
        self.mes=mes
        self.cambiocecos = cambiocecos # diccionarios cambios en los cecos.
        self.cambio_centro = cambio_centro
    def _distribucionagrupmes(self): # realiza ajustes en la afo de distragrupames
        nomcol = ['Codigo Clasificacion','Codigo Detalle Clasi',
               'Codigo tipo de Gasto','Centro de Costo','Nombre_centro_costes',
               'Concepto (Cl.C)','Nombre_concepto','Subc. (Cl.C)','Nombre_subconc',
               'Pool de recursos','Nombre_Pol_recur','Oficina de ventas','Nombre_of_ventas',
               'Codigo Agrupa Region','Ramo','Nombre_ramo','Linea Marca','Cliente','Nombre_cliente',
               'Codigo tipo de Centr','Agrupo centros de co','Codigo agrupa region','Clase de coste',
               'Ejercicio/Período','Gasto_Agrup'+ self.mes,'Valor Total Moneda Total']
        distiagrupames = dfarchivoAFO(self.disagrupmes,1,nomcol)

        distiagrupames['Gasto_Agrup'+ self.mes]=distiagrupames['Gasto_Agrup'+ self.mes].astype(float)
        if len (self.cambiocecos) > 0:
            distiagrupames = reemplazo_valores(distiagrupames,self.cambiocecos,'Centro de Costo','Codigo tipo de Gasto')
            distiagrupames = reemplazo_valores(distiagrupames,self.cambio_centro,'Centro de Costo','Codigo tipo de Centr')
           

        distiagrupames = distiagrupames[distiagrupames['Codigo tipo de Gasto']!='99']
        validacionagrupa = distiagrupames.groupby('Centro de Costo')['Gasto_Agrup'+ self.mes].sum()
        validacionagrupa = validacionagrupa.reset_index()
    
        return validacionagrupa
    
    def _distribionmes(self): # realiza ajustes en la afo de distrames
        nomcol =['Centro de Costo','Nombre_centro_costes','Clase de coste',
                  'Nombre_ClaseCoste','Concepto','Nombre_Concepto','SubConcpeto',
                  'Nombre_SubConp','Pool de recursos','Nombre_pool_recur','Oficina de ventas',
                  'Nombre_of_ventas','ramo','Nombre_ramo','Cliente','Gasto_'+self.mes]
        
        distrimes = dfarchivoAFO(self.dismes ,1,nomcol)

        distrimes['Gasto_'+self.mes]=distrimes['Gasto_'+self.mes].astype(float)
        vlidaciondismes = distrimes.groupby(['Centro de Costo','Nombre_centro_costes'])['Gasto_'+self.mes].sum()
        vlidaciondismes = vlidaciondismes.reset_index()
        return vlidaciondismes
    
    def validacionCecos(self):

        cecomes = self._distribionmes()
        cecoagrupa = self._distribucionagrupmes()

       
        cecomes = pd.merge(cecoagrupa,cecomes, on='Centro de Costo',
                           how='outer')        
        #del cecomes['Centro de coste']
        cecomes['Gasto_'+self.mes] = cecomes['Gasto_'+self.mes].fillna(0)
        cecomes['Gasto_Agrup'+ self.mes] = cecomes['Gasto_Agrup'+ self.mes].fillna(0)
        cecomes['Nombre_centro_costes']=cecomes['Nombre_centro_costes'].fillna('-')
        cecomes = cecomes[['Centro de Costo','Nombre_centro_costes','Gasto_Agrup'+ self.mes,'Gasto_'+self.mes]]
        cecomes['Diferencia'] = cecomes['Gasto_'+self.mes]-cecomes['Gasto_Agrup'+ self.mes]
        cecomes=cecomes.sort_values(['Diferencia','Centro de Costo'], ascending=[False,True])    
     
        return cecomes

