def clean_text(df, column_name):
    # Eliminar primeras palabras hasta el primer "\n"
    result = df[column_name].str.replace(r"^[^\n]*\n", "", regex=True)

    # Convertir a minúsculas
    result = result.str.lower()

    # TODO: completar signos de puntuación faltantes
    #   Estaria dejando el ' puesto que pueden existir palabras como don't
    for punc in ["[", r"\n", ",", ":", "?", '!', '$', '%', '&', '(', ')', '*', '+', '-', '.', '/', ';', '@', ']', r'\r']:
        result = result.str.replace(punc, " ")

    return result


def search_punctuation(df, column_name):
    # Importo los modulos necesarios
    import pandas as pd
    import re
    import string

    # Concatenar todos los textos en uno solo
    texto = ' '.join(df[f'{column_name}'])

    # Extraer todos los signos de puntuacion
    signos = re.findall(f'[{re.escape(string.punctuation)}]', texto)

    # Obtener un set ordenado de signos unicos encontrados
    return sorted(set(signos))


def clean_names(df, column_name):
    # Para eliminar el nombre de los candidatos de los discursos
    text = df[column_name]
    for name in ['bernie', 'sanders', 'donald', 'trump', 'joe', 'biden', 'kamala', 'harris', 'mike', 'pence']:
        text = text.str.replace(name, '')

    return text
