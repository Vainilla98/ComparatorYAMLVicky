import re

from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import DoubleQuotedScalarString as Comillas

from deepdiff import DeepDiff
import os
from io import StringIO

from translator import traducir
from config import crear_configuracion, obtener_rutas, traducir_si_no, idiomas_origen_destino

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
        contenido = yaml.load(fp)
    return contenido


def procesar_diferencias(ddiff: dict, ruta_ingles: str, trans_lang: str) -> str:
    """Procesa las diferencias y las devuelve en formato de texto."""
    resultado = StringIO()

    if "dictionary_item_removed" in ddiff:
        resultado.write(titulo("NUEVOS"))
        for e in ddiff["dictionary_item_removed"]:
            resultado.write(f" - {e[19:-2]}\n")

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
                output: dict = yaml.load(f)

            for elemento in output[trans_lang]:
                final[trans_lang][elemento] = Comillas(output[trans_lang][elemento])

            for clave, traduccion in traducciones_automaticas:
                final[trans_lang][clave] = Comillas(traduccion)

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


crear_configuracion()

path_mod_steam, path_mod_vicky = obtener_rutas()
original_lang, translation_lang = idiomas_origen_destino()

if path_mod_vicky is None:
    print("Error in the configuration file. Cannot read the local mod path")
    exit(1)

if path_mod_steam is None:
    print("Error in the configuration file. Cannot read the Steam mod path")
    exit(2)

if original_lang is None:
    print("Error in the configuration file. Cannot read the original language")
    exit(3)

if translation_lang is None:
    print("Error in the configuration file. Cannot read the target language")
    exit(4)

if not os.path.exists(path_mod_steam):
    print(f"This path does not exist: {path_mod_steam}")
    exit(5)

if not os.path.exists(path_mod_vicky):
    print(f"This path does not exist: {path_mod_vicky}")
    exit(6)


# Ejecutar la comparación y escribir el resultado en un archivo
res = comparar_archivos(path_mod_vicky, path_mod_steam, original_lang, translation_lang)

with open(os.path.join(os.getcwd(), 'res.txt'), 'w', encoding="utf-8") as file:
    file.write(res)
