import os
import sys
from loguru import logger


class ConfigPathRoutes:
    """
    Clase responsable de configurar las rutas del proyecto para asegurar que los módulos y paquetes sean correctamente detectados y importados, evitando problemas de detección y conflictos en los imports.
    """
    # atributos de clase
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    @classmethod
    def modificar_path(cls):
        """
        Modifica el sistema de búsqueda de módulos (`sys.path`) añadiendo las rutas del directorio actual y su directorio padre.

        Esta operación es útil para garantizar que se puedan importar módulos de forma coherente desde cualquier
        parte del proyecto.
        """
        sys.path.append(cls.current_dir)
        sys.path.append(cls.parent_dir)

    @classmethod
    def resolver_rutas(cls, *subrutas):
        """
        Resuelve y devuelve una ruta absoluta combinando el directorio actual con los argumentos proporcionados.

        Args:
            *args: Componentes de la ruta a combinar.

        Returns:
            str: Ruta absoluta resultante.
        """
        return os.path.normpath(os.path.join(cls.current_dir, *subrutas))

def setup_logger():
    
    logger.remove()  # elimina el handler por defecto

    # Colores
    logger.add(
        sys.stdout,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{message}</level>",
    )

    # Archivo → desarrollador (sin colores, con contexto)
    logger.add(
        "logs/app.log",
        level="DEBUG",
        format="{time} | {level} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        retention="7 days",
        compression="zip"
    )


ConfigPathRoutes.modificar_path()