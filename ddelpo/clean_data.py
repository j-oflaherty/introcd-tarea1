# Importo los modulos necesarios
import re
import string
import pandas as pd


def clean_text(df, column_name):
    # Eliminar primeras palabras hasta el primer "\n"
    result = df[column_name].str.replace(r"^[^\n]*\n", "", regex=True)

    # Convertir a minúsculas
    result = result.str.lower()

    # TODO: completar signos de puntuación faltantes
    #   Estaría dejando el ' puesto que pueden existir palabras como don't
    for punc in [
        "[", r"\n", ",", ":", "?",
        '!', '$', '%', '&', '(', ')', '*', '+', '-', '.', '/', ';', '@', '[', r'\r'
    ]:
        result = result.str.replace(punc, " ")

    return result


def search_punctuation(df: pd.DataFrame, column_name: str) -> set:
    # Concatenar todos los textos en uno solo
    texto = ' '.join(df[f'{column_name}'])

    # Extraer todos los signos de puntuación
    signos = re.findall(f'[{re.escape(string.punctuation)}]', texto)

    # Obtener un set de signos únicos encontrados
    return set(signos)


def list_of_tuples(lista: list) -> list:
    return list(zip(lista[::2], lista[1::2]))
