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


# Función para extraer el estado de la columna location
def get_state(location):
    us_states_list = [
        "alabama",
        "alaska",
        "arizona",
        "arkansas",
        "california",
        "colorado",
        "connecticut",
        "delaware",
        "florida",
        "georgia",
        "hawaii",
        "idaho",
        "illinois",
        "indiana",
        "iowa",
        "kansas",
        "kentucky",
        "louisiana",
        "maine",
        "maryland",
        "massachusetts",
        "michigan",
        "minnesota",
        "mississippi",
        "missouri",
        "montana",
        "nebraska",
        "nevada",
        "new hampshire",
        "new jersey",
        "new mexico",
        "new york",
        "north carolina",
        "north dakota",
        "ohio",
        "oklahoma",
        "oregon",
        "pennsylvania",
        "rhode island",
        "south carolina",
        "south dakota",
        "tennessee",
        "texas",
        "utah",
        "vermont",
        "virginia",
        "washington",
        "west virginia",
        "wisconsin",
        "wyoming"
    ]

    if not isinstance(location, str):
        return None
    location = location.split(",")
    if len(location) == 2:
        return location[1].strip()
    if location[0].lower() in us_states_list:
        return location[0]
    else:
        return None
