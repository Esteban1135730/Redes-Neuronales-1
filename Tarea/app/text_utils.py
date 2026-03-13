import re

def limpiar_texto(texto):
    if not isinstance(texto, str):
        return ""
    # Convertir a minúsculas
    texto = texto.lower()
    # Eliminar enlaces
    texto = re.sub(r'http\S+', '', texto)
    # Eliminar menciones y hashtags
    texto = re.sub(r'@\w+|#\w+', '', texto)
    # Eliminar caracteres especiales y números
    texto = re.sub(r'[^a-zA-Záéíóúüñ\s]', '', texto)
    # Eliminar espacios extras
    texto = " ".join(texto.split())
    return texto