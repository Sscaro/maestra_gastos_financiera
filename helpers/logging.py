'''
modulo para loger de confirmación
'''
import logging

def get_my_logger(name='my_logger'):
    '''
    Obtiene un logger configurado para mostrar mensajes en la consola

    Args:
    name (str): Nombre del logger a crear. Por defecto es 'my_logger'

    Returns:
    logger (logging.Logger): Un logger configurado para mostrar mensajes en la consola con el formato
        '%(asctime)s - %(message)s' y el nivel de logueo INFO
    '''

    # Crear un logger
    logger = logging.getLogger(name)

    # Configurar el logger si no tiene handlers
    if not logger.hasHandlers():
        logger.setLevel(logging.INFO)
        # Formato del mensaje
        formatter = logging.Formatter(
            '%(asctime)s - %(message)s',
            datefmt='%d-%b-%y %H:%M:%S'
        )
        # Crear y añadir un StreamHandler
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger
