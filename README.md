# maestra_gastos_financiera
Resumen de desarrollo
Objetivo
Actualizar Maestra de gastos con la logica correspondiente a las reglas de negocio
y particularidades presentes en los datos suministrados

Inusmos:
- Real Ppto Historico: Archivo en formato .xlsx con el consolidado del gasto real mes a mes y el ppto mes a mes
- data Agrupaciones: Archivo usualmente descargado de Analysis for office con información del gasto real
- Data distribucion: Archivo usualmente desacrgado de Analysis for office con información del gasto real


Ejecutar proyecto
python main.py 
(se debe tener python instalado, instalar las librerias del archivo requirementes)
pip install -r requirements.txt


Recomendacion
Ajustar python embebido si no se peude instalar python 
(Preguntar por desarrollador)

Archivos de configuración;
config: Parametros y logicas de las diferentes tablas 
    Nombres, tipo de datos, exclusiones, logicas de uniones y agrupaciones
    (Usuario debe conocer estas logicas y modificarlas de acuerdo a actualizacion en reglas de negocio)
reemplazos: Parametros para reemplazar inconsistencias en los datos originales 
    (Usuario debe conocer estas logicas y modificarlas de acuerdo a actualizacion en reglas de negocio)
condigcecos: Cecos a tener en consideración y que no cumplen con la parametrización definida desde los modelos del gasto

Se recomienda mover el proyecto a un ambiente embedido en caso contrario se debe instalar ciertas librerias, 

