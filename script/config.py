import configparser as cfg
import os

# Ruta por defecto donde se va a almacenar la configuración
FICHERO_CONFIGURACION: str = "config.ini"

# Creamos el objeto de ConfigParser de manera global
config: cfg.ConfigParser = cfg.ConfigParser()


def existe_fichero(fichero: str = FICHERO_CONFIGURACION) -> bool:
    return os.path.exists(fichero) and os.path.isfile(fichero)


def crear_configuracion(fichero: str = FICHERO_CONFIGURACION):
    """
    Crea el fichero de configuración con los valores por defecto de cada seccion del fichero si no tiene
    la sección creada

    :param fichero: El fichero de configuración
    """
    # Leemos la configuración
    config.read(fichero)

    # Revisa si tiene la seccion ya creada. Si no la crea y le da el valor por defecto
    if not config.has_section("CAMBIOS"):
        config.add_section("CAMBIOS")

    if not config.has_option('CAMBIOS', "path_mod_steam"):
        config.set('CAMBIOS', "path_mod_steam", "C:/Program Files (x86)/Steam/steamapps/workshop/content/529340")
    if not config.has_option('CAMBIOS', "path_mod_vicky"):
        config.set('CAMBIOS', "path_mod_vicky",
                   "C:/User/User/Documents/Paradox Interactive/Victoria 3/mod/L'amour a Espagne")
    if not config.has_option('CAMBIOS', "translate"):
        config.set('CAMBIOS', "translate", "True")
    if not config.has_option('CAMBIOS', "original_lang"):
        config.set('CAMBIOS', "original_lang", "spanish")
    if not config.has_option('CAMBIOS', "translation_lang"):
        config.set('CAMBIOS', "translation_lang", "english")

    with open(fichero, 'w') as con:
        config.write(con)


def obtener_rutas(fichero: str = FICHERO_CONFIGURACION) -> (str, str):
    """
    Devuelve la configuracion de la sección "IA" en el fichero de cofiugración

    :param fichero: El fichero de configuracion
    :return: Una tupla con la configuracion
    """
    # Read the configuration file
    config_str: list[str] = config.read(fichero)

    if len(config_str) != 0:
        path_mod_steam = config.get('CAMBIOS', 'path_mod_steam')
        path_mod_vicky = config.get('CAMBIOS', 'path_mod_vicky')
    else:
        path_mod_steam = None
        path_mod_vicky = None

    return path_mod_steam, path_mod_vicky


def traducir_si_no(fichero: str = FICHERO_CONFIGURACION) -> bool:
    """
    Devuelve la configuracion de la sección "IA" en el fichero de cofiugración

    :param fichero: El fichero de configuracion

    """
    # Read the configuration file
    config_str: list[str] = config.read(fichero)

    translate = config.getboolean('CAMBIOS', 'translate') if len(config_str) != 0 else False

    return translate


def idiomas_origen_destino(fichero: str = FICHERO_CONFIGURACION) -> (str, str):
    """
    Devuelve la configuracion de la sección "IA" en el fichero de cofiugración

    :param fichero: El fichero de configuracion
    """
    # Read the configuration file
    config_str: list[str] = config.read(fichero)

    if len(config_str) != 0:
        original_lang = config.get('CAMBIOS', 'original_lang')
        translation_lang = config.get('CAMBIOS', 'translation_lang')
    else:
        original_lang = None
        translation_lang = None

    return original_lang, translation_lang
