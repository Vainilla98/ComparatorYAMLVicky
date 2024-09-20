import re
import sys
import traceback

from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import DoubleQuotedScalarString as Comillas

from deepdiff import DeepDiff
import os
from io import StringIO

from translator import traducir
from config import crear_configuracion, obtener_rutas, traducir_si_no, idiomas_origen_destino, existe_fichero

yaml = YAML()
yaml.width = 90000000
yaml.preserve_quotes = True
yaml.indent(mapping=1)


def titulo(texto: str, tipo: str = "*") -> str:
    if tipo == "*":
        return (f"                   {texto.ljust(53)}\n"
                "+ ---------------------------------------------------------"
                "--------------------- +\n")
    else:
        return (f"\n+ ------------------------------------------------------------------------------ +\n"
                f"|                          {texto.ljust(54)}|\n"
                "+ ------------------------------------------------------------------------------ +\n")


def yaml_as_dict(my_file: str) -> dict:
    """Carga un archivo YAML y lo convierte en un diccionario."""
    with open(my_file, 'r', encoding="utf-8") as fp:
        contenido = re.sub(r":\d", ":", fp.read())
        contenido = yaml.load(contenido)
    return contenido


def procesar_diferencias(ddiff: dict, ruta_ingles: str, trans_lang: str) -> str:
    """Procesa las diferencias y las devuelve en formato de texto."""
    resultado = StringIO()

    if "dictionary_item_added" in ddiff:
        resultado.write(titulo("NUEVOS"))
        for e in ddiff["dictionary_item_added"]:
            resultado.write(f" - {e[19:-2]}\n")

    if "dictionary_item_removed" in ddiff:
        resultado.write(f"\n{titulo("QUITADOS")}")
        for e in ddiff["dictionary_item_removed"]:
            resultado.write(f" - {e[19:-2]}\n")

    # if "dictionary_item_added" in ddiff:
    #     resultado.write(titulo("QUITADOS"))
    #     for e in ddiff["dictionary_item_added"]:
    #         resultado.write(f" - {e}\n")

    if "values_changed" in ddiff:
        resultado.write(f"\n{titulo("CAMBIADOS")}")
        traducciones_automaticas: list[tuple[str, str]] = []
        for e in ddiff["values_changed"]:
            clave = e[19:-2]
            old_value = ddiff["values_changed"][e]["old_value"].replace("\n", "\\n")
            new_value = ddiff["values_changed"][e]["new_value"].replace("\n", "\\n")
            if traducir_si_no() and os.path.exists(ruta_ingles) and not re.search(r"[\[\]$]", new_value):
                match trans_lang:
                    case "braz_por":
                        idioma = "pt"
                    case "french":
                        idioma = "fr"
                    case "german":
                        idioma = "de"
                    case "japanese":
                        idioma = "ja"
                    case "korean":
                        idioma = "ko"
                    case "polish":
                        idioma = "pl"
                    case "russian":
                        idioma = "ru"
                    case "simp_chinese":
                        idioma = "zh-cn"
                    case "spanish":
                        idioma = "es"
                    case "turkish":
                        idioma = "tr"
                    case _:
                        idioma = "en"

                traduccion: str = traducir(new_value, idioma)
                traducciones_automaticas.append((clave, traduccion))
                new_value = f"{new_value}\n\t\t * {traduccion}"
            resultado.write(f" - {clave}\n\t > Old: {old_value}\n\t > New: {new_value}\n")

        if len(traducciones_automaticas) > 0:
            final: dict = {f"l_{trans_lang}": {}}
            with open(ruta_ingles, 'r', encoding="utf-8") as f:
                contenido = re.sub(r":\d", ":", f.read())
                output: dict = yaml.load(contenido)

            for elemento in output[f"l_{trans_lang}"]:
                final[f"l_{trans_lang}"][elemento] = Comillas(output[f"l_{trans_lang}"][elemento])

            for clave, traduccion in traducciones_automaticas:
                final[f"l_{trans_lang}"][clave] = Comillas(traduccion)

            with open(ruta_ingles, 'w', encoding="utf-8") as f:
                yaml.dump(final, f)

    return resultado.getvalue()


def comparar_archivos(dir_nuevo: str, dir_viejo: str, orig_lang: str, trans_lang: str) -> str:
    """Compara los archivos en dos directorios y devuelve un reporte de diferencias."""
    resultado = StringIO()

    for path, _, files in os.walk(f"{dir_nuevo}\\localization\\{orig_lang}"):
        for name in files:
            ruta_nuevo = os.path.join(path, name)
            ruta_viejo = os.path.join(dir_viejo, "localization", orig_lang, name)
            ruta_viejo_replace = os.path.join(dir_viejo, "localization", orig_lang, "replace", name)

            # print(f"{ruta_nuevo} -> {ruta_viejo}")

            if os.path.exists(ruta_viejo_replace):
                ruta_viejo = ruta_viejo_replace

            resultado.write(titulo(name, tipo="+"))

            if os.path.exists(ruta_viejo):
                a = yaml_as_dict(ruta_viejo)
                b = yaml_as_dict(ruta_nuevo)

                ddiff = DeepDiff(a, b)
                fichero_ingles = os.path.join(dir_nuevo, "localization", trans_lang,
                                              name.replace(f"l_{orig_lang}", f"l_{trans_lang}"))
                resultado.write(procesar_diferencias(ddiff, fichero_ingles, trans_lang))
            else:
                resultado.write(f" {ruta_viejo} es un nuevo fichero\n")

    return resultado.getvalue()


existe_fichero: bool = existe_fichero()

crear_configuracion()

if existe_fichero:
    path_mod_old, path_mod_new = obtener_rutas()
    original_lang, translation_lang = idiomas_origen_destino()

    if path_mod_new is None:
        print("Error in the configuration file. Cannot read the local mod path")
        sys.exit(1)

    if path_mod_old is None:
        print("Error in the configuration file. Cannot read the Steam mod path")
        sys.exit(2)

    if original_lang is None:
        print("Error in the configuration file. Cannot read the original language")
        sys.exit(3)

    if translation_lang is None:
        print("Error in the configuration file. Cannot read the target language")
        sys.exit(4)

    if not os.path.exists(path_mod_old):
        print(f"This path does not exist: {path_mod_old}")
        sys.exit(5)

    if not os.path.exists(path_mod_new):
        print(f"This path does not exist: {path_mod_new}")
        sys.exit(6)

    if not os.path.exists(os.path.join(path_mod_old, "localization")):
        print(f"Isn't the correct previous mod folder: {os.path.join(path_mod_old, "localization")}")
        sys.exit(7)

    if not os.path.exists(os.path.join(path_mod_new, "localization")):
        print(f"Isn't the correct updated mod folder: {os.path.join(path_mod_new, "localization")}")
        sys.exit(8)

    # Ejecutar la comparación y escribir el resultado en un archivo
    try:
        res = comparar_archivos(path_mod_new, path_mod_old, original_lang, translation_lang)
        with open(os.path.join(os.getcwd(), 'res.txt'), 'w', encoding="utf-8") as file:
            file.write(res[1:])  # El '1:' es para quitar el primer salto de línea
        print("res.txt created successfully")
    except Exception as ex:
        traceback.print_exception(ex)
    finally:
        sys.exit(100)
else:
    print(".ini confiuration file created successfully in the current directory")
