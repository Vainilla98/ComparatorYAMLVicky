from googletrans import Translator

__translator = Translator()


def traducir(texto: list[str] | str = 'Tus ojos, espadas dentro de mi carne', idioma: str = 'en') -> str:
    return __translator.translate(texto, dest=idioma, src="es").text
