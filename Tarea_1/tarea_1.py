# %% Importamos los módulos a utilizar
import locale
import re
import sys

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from wordcloud import STOPWORDS

from utils.clean_data import clean_text, list_of_tuples, search_punctuation
from utils.location_analysis import execute as execute_location_analysis
from utils.plots import (
    circle_packing_plot,
    directed_graph_plot,
    stacked_bar_plot,
    word_cloud_plot,
)

# %% Letra para que coincida con LaTex
plt.rcParams.update(
    {
        "font.family": "Latin Modern Roman",
        "mathtext.fontset": "cm",
        "figure.titlesize": 18,
        "axes.titlesize": 16,
        "axes.labelsize": 14,
        "xtick.labelsize": 12,
        "ytick.labelsize": 12,
        "legend.title_fontsize": 16,
        "legend.fontsize": 14,
    }
)

# %% DataFrame con todos los discursos
df_speeches = pd.read_csv(
    filepath_or_buffer=r"data/us_2020_election_speeches.csv", sep=","
)

# Tipos de datos
print(df_speeches.dtypes)
df_speeches["date"] = pd.to_datetime(df_speeches["date"], format="%b %d, %Y")

# Datos faltantes
print(df_speeches.isna().sum())

# Cantidad de discursos por tipo
print(df_speeches.groupby("type").size().sort_values(ascending=False))

# Cantidad de discursos por ubicación
# La mayoría fueron virtuales por el COVID-19
print(df_speeches.groupby("location").size().sort_values(ascending=False))

# %% Analice la cantidad de discursos por candidato
n_speeches = df_speeches.groupby("speaker").size().sort_values(ascending=False)

# Quiero ver todos los oradores
print(df_speeches.speaker.unique())

# %% Gráfico de burbujas con la cantidad de discursos por candidato
print("Procesando gráfico de burbujas...")
circle_packing_plot(ds=n_speeches, save_path="img/speaker_analysis.png")

# %% Veo que hay discursos donde hay más de un candidato en la columna 'speaker'
# Como veo que están los nombres separados por ',' quiero ver si es significativa la cantidad de registros
print(len(df_speeches[df_speeches["speaker"].str.contains(",", na=False)]))

# También veo otros registros donde no se identifica al candidato
print(len(df_speeches[df_speeches["speaker"] == "Multiple Speakers"]))
print(len(df_speeches[df_speeches["speaker"] == "Democratic Candidates"]))
print(len(df_speeches[df_speeches["speaker"] == "???"]))

# %% Hay 31 registros en los que no es posible determinar el orador por la columna 'speaker'
# Voy a generar un DataFrame cuya estructura sea una fila por intervención de cada orador
# Es decir que un discurso va a tener más de una fila
df_speeches_2 = df_speeches.copy()

# Elimino lo que está entre [] como [crosstalk...], [inaudible...], etc.
df_speeches_2["text"] = df_speeches_2["text"].str.replace(r"\[.*?\]", "", regex=True)

# Este comercial en particular me rompe el index 79 donde quiero separar las intervenciones
df_speeches_2["text"] = df_speeches_2["text"].str.replace("Commercial: (48:14)\r\n", "")

# Elimino el patrón ': (mm:ss)'
df_speeches_2["text"] = df_speeches_2["text"].str.replace(
    r": \(\d{2}:\d{2}\)", "", regex=True
)

# Elimino el patrón ': (hh:mm:ss)'
df_speeches_2["text"] = df_speeches_2["text"].str.replace(
    r": \(\d{2}:\d{2}\:\d{2}\)", "", regex=True
)

# Convierto la columna en una lista donde cada elemento es una intervención de un orador
# Hay que aplicar un regex si es Mac y otro si es Windows
if sys.platform == "win32":
    df_speeches_2["text"] = df_speeches_2["text"].str.split(
        r"\r\n(?:\xa0\r\n)?", regex=True
    )
else:
    df_speeches_2["text"] = df_speeches_2["text"].str.split(
        r"[(\r\n)\n](?:\xa0[(\r\n)\n])?", regex=True
    )

# Convierto la lista en una lista de tuplas donde cada tupla tiene el par orador-discurso
df_speeches_2["text"] = df_speeches_2["text"].apply(list_of_tuples)

# Con explode hago que cada elemento de la lista (cada tupla) sea una fila
df_speeches_2 = df_speeches_2.explode("text")

# Sobreescribo los valores de speaker y text con los valores de cada tupla
df_speeches_2[["speaker", "text"]] = pd.DataFrame(
    df_speeches_2["text"].tolist(), index=df_speeches_2.index
)

# Chequeo con los index que la cantidad de discursos sigue siendo la misma
print(len(df_speeches_2.index.unique()))

# %% Ejemplo 1: Cuántos oradores intervienen en 'Multiple Speakers'
for i in df_speeches[df_speeches["speaker"] == "Multiple Speakers"].index:
    print(len(df_speeches_2.loc[i].speaker.unique()))

# %% Ejemplo 2: Cuántos oradores intervienen en 'Democratic Candidates'
for i in df_speeches[df_speeches["speaker"] == "Democratic Candidates"].index:
    print(len(df_speeches_2.loc[i].speaker.unique()))

# %% Ejemplo 3: Cuántos oradores intervienen en '???'
for i in df_speeches[df_speeches["speaker"] == "???"].index:
    print(len(df_speeches_2.loc[i].speaker.unique()))

# %% Ejemplo 4: Cuántos oradores intervienen en NaN
for i in df_speeches[df_speeches["speaker"].isna()].index:
    print(len(df_speeches_2.loc[i].speaker.unique()))

# %% Quiero ver los candidatos que me quedaron
# df_speeches_2.to_excel(r'data/speeches.xlsx')

# %% Top 5 candidatos con más discursos
top_5 = list(n_speeches.head(5).index)

# Quiero ver como aparecen los 5 principales candidatos
print(
    df_speeches_2[df_speeches_2["speaker"].str.contains("Trump", na=False)][
        "speaker"
    ].unique()
)
print(
    df_speeches_2[df_speeches_2["speaker"].str.contains("Biden", na=False)][
        "speaker"
    ].unique()
)
print(
    df_speeches_2[df_speeches_2["speaker"].str.contains("Pence", na=False)][
        "speaker"
    ].unique()
)
print(
    df_speeches_2[df_speeches_2["speaker"].str.contains("Harris", na=False)][
        "speaker"
    ].unique()
)
print(
    df_speeches_2[df_speeches_2["speaker"].str.contains("Sanders", na=False)][
        "speaker"
    ].unique()
)

# Homogeneizar nombres
names = {
    "President Trump": "Donald Trump",
    "President Donald J. Trump": "Donald Trump",
    "President Donald Trump": "Donald Trump",
    "Donald J. Trump": "Donald Trump",
    "Trump": "Donald Trump",
    "Vice President Joe Biden": "Joe Biden",
    "VIce President Biden": "Joe Biden",
    "Joe Biden ": "Joe Biden",
    "Vice President Mike Pence": "Mike Pence",
    "Vice President Mike Pence ": "Mike Pence",
    "Kamala Harris ": "Kamala Harris",
    "Senator Kamala Harris": "Kamala Harris",
    "Senator Harris": "Kamala Harris",
    "Senator Bernie Sanders": "Bernie Sanders",
    "Sanders": "Bernie Sanders",
}
df_speeches_2["speaker"] = (
    df_speeches_2["speaker"].map(names).fillna(df_speeches_2["speaker"])
)

# %% Para chequear escala temporal
print(df_speeches_2["date"].min())
print(df_speeches_2["date"].max())
df_speeches_2["week"] = (
    df_speeches_2["date"].dt.to_period("W").apply(lambda x: x.start_time)
)

# %% Me quedo con las intervenciones del top 5
df_speeches_top_5 = df_speeches_2[df_speeches_2["speaker"].isin(top_5)].copy()

# %% Datos faltantes
print(df_speeches_top_5.isna().sum())

# %% Asignar partido politico
parties = {
    "Joe Biden": "Partido Demócrata",
    "Kamala Harris": "Partido Demócrata",
    "Bernie Sanders": "Partido Demócrata",
    "Donald Trump": "Partido Republicano",
    "Mike Pence": "Partido Republicano",
}
df_speeches_top_5["party"] = df_speeches_top_5["speaker"].map(parties)

# %% Establecer a idioma español para que las fechas de las gráficas queden en ese idioma
locale.setlocale(locale.LC_TIME, locale="es_ES.UTF-8")

# %% Visualización de los discursos de cada candidato a lo largo del tiempo
df = (
    df_speeches_top_5.groupby(["week", "speaker"])
    .apply(lambda x: x.index.nunique(), include_groups=False)
    .reset_index(name="speeches")
    .sort_values("week")
)
df_pivot = df.pivot(index="week", columns="speaker", values="speeches").fillna(0)
df_pivot = df_pivot[
    ["Joe Biden", "Kamala Harris", "Bernie Sanders", "Donald Trump", "Mike Pence"]
]
df_pivot.index = df_pivot.index.strftime("%b %d")
stacked_bar_plot(
    df=df_pivot,
    save_path="img/discursos_candidatos_por_semana.png",
    color=["#1f77b4", "#4e9cd5", "#8fbadd", "#d62728", "#e96a6a"],
    plot_title="Discursos por Candidato en el Año 2020",
    xlabel="Semana",
    ylabel="Cantidad de Discursos",
    ylim_top=24,
)

# %% Busco los signos de puntuación que existen para después agregarlos a la función clean_text
print(search_punctuation(df=df_speeches_top_5, column_name="text"))

# %% Creamos una nueva columna CleanText a partir de text
df_speeches_top_5["clean_text"] = clean_text(df=df_speeches_top_5, column_name="text")

# %% Convierte párrafos en listas 'palabra1 palabra2 palabra3' -> ['palabra1', 'palabra2', 'palabra3']
df_speeches_top_5["word_list"] = df_speeches_top_5["clean_text"].str.split()

# Veamos la nueva columna creada: notar que a la derecha tenemos una lista: [palabra1, palabra2, palabra3]
print(df_speeches_top_5[["clean_text", "word_list"]])

# %% Realice una visualización que permita comparar las palabras más frecuentes de cada uno de los cinco candidatos/as.
df = (
    df_speeches_top_5.groupby("speaker")["clean_text"]
    .apply(lambda x: " ".join(x))
    .reset_index()
)

# Crear un colormap personalizado de rojo a azul
us_cmap = LinearSegmentedColormap.from_list(
    name="us_flag", colors=["#d62728", "#1f77b4"]
)

# Para eliminar palabras comunes del idioma que no aportan (agrego otras que no trae el módulo worldcloud)
STOPWORDS.update(
    [
        "s",
        "re",
        "don",
        "didn",
        "know",
        "will",
        "going",
        "need",
        "t",
        "people",
        "think",
        "want",
        "well",
        "let",
        "said",
        "thank",
        "one",
    ]
)

# %% Creo una nube por candidato con las 100 palabras más dichas
word_cloud_plot(
    df=df,
    save_path="img/wordcloud_por_candidato.png",
    plot_title="TOP 100 de Palabras más Utilizadas por Candidato",
    colormap=us_cmap,
    stopwords=STOPWORDS,
    max_words=100,
    text="clean_text",
    speaker="speaker",
)

# El problema en los resultados son las palabras comunes
# Esas palabras quitan el foco de otras palabras que pueden indicar los tópicos que cada candidato considera más relevantes

# %% Busque los candidatos/as con mayor cantidad de palabras.
df_speeches_top_5["n_words"] = df_speeches_top_5["word_list"].apply(lambda x: len(x))
print(
    df_speeches_top_5.groupby("speaker")["n_words"].sum().sort_values(ascending=False)
)

# %% Formas de mencionar a los candidatos
menciones = {
    "Joe Biden": [
        r"\bjoe biden\b",
        r"\bbiden\b",
        r"\bvice president biden\b",
        r"\bvice president joe biden\b",
    ],
    "Donald Trump": [
        r"\bdonald trump\b",
        r"\btrump\b",
        r"\bpresident trump\b",
        r"\bpresident donald\b",
        r"\bdonald\b",
    ],
    "Mike Pence": [r"\bmike pence\b", r"\bpence\b", r"\bvice president pence\b"],
    "Bernie Sanders": [r"\bbernie sanders\b", r"\bsanders\b"],
    "Kamala Harris": [
        r"\bkamala harris\b",
        r"\bharris\b",
        r"\bsenator harris\b",
        r"\bkamala\b",
    ],
}

# Construya una matriz de 5x5, donde cada fila y columna corresponden a un candiato/a,
# y la entrada (i,j) contiene la cantidad de veces que el candiato/a “i” menciona al candiato/a “j”.
mentions_matrix = pd.DataFrame(data=0, index=top_5, columns=top_5)
for _, row in df.iterrows():
    candidato = row["speaker"]
    discursos = row["clean_text"]
    for nombre_mencionado, patrones in menciones.items():
        # Para evitar menciones a sí mismo
        # if nombre_mencionado == candidato:
        #     continue

        # Arranco la cuenta de los patrones de texto en los discursos
        total = 0
        for patron in patrones:
            coincidencias = re.findall(patron, discursos)
            total += len(coincidencias)

        # Lo agrego a la matriz
        mentions_matrix.loc[candidato, nombre_mencionado] = total

# %% Opcional: Genere un grafo dirigido con esa matriz de adyacencia para visualizar las menciones.
colores_por_candidato = {
    "Bernie Sanders": "#8fbadd",
    "Donald Trump": "#d62728",
    "Joe Biden": "#1f77b4",
    "Kamala Harris": "#4e9cd5",
    "Mike Pence": "#e96a6a",
}
directed_graph_plot(
    df=mentions_matrix,
    save_path="img/graph.png",
    plot_title="Grafo Dirigido de Menciones entre Candidatos",
    colors=colores_por_candidato,
)

# %% Creo la categoría Otros
df_speeches_2["speaker_2"] = df_speeches_2["speaker"].apply(
    lambda x: "Otros" if x not in top_5 else x
)
grp_otros = list(
    df_speeches_2.loc[df_speeches_2["speaker_2"] == "Otros"]["speaker"].unique()
)

# Así saco lo que empiece con Speaker
grp_otros = [nombre for nombre in grp_otros if not nombre.strip().startswith("Speaker")]

# Así saco lo que tenga Moderator y Crowd
grp_otros = [nombre for nombre in grp_otros if "Moderator" not in nombre]
grp_otros = [nombre for nombre in grp_otros if "Crowd" not in nombre]

# Lista de políticos identificados en el grupo Otros
politicos = [
    "Joe Biden",
    "Kamala Harris",
    "Bernie Sanders",
    "Donald Trump",
    "Mike Pence",
    "Alex Padilla",
    "Alexandria Ocasio-Cortez",
    "Amy Klobuchar",
    "Andrew Cuomo",
    "Andrew Yang",
    "Barack Obama",
    "Ben Carson",
    "Beto O’Rourke",
    "Bill Clinton",
    "Bob Casey",
    "Brendan Boyle",
    "Brenda Lawrence",
    "Carol Moseley Braun",
    "Catherine Cortez Masto",
    "Cedric Richmond",
    "Chuck Hagel",
    "Chuck Schumer",
    "Colin Allred",
    "Colin Powell",
    "Conor Lamb",
    "Cory Booker",
    "Cory Gardner",
    "David Perdue",
    "David Zuckerman",
    "Debbie Mucarsel-Powell",
    "Deb Haaland",
    "Doug Ducey",
    "Doug Jones",
    "Donna Brazile",
    "Donald Trump Jr.",
    "Elise Stefanik",
    "Elizabeth Warren",
    "Eric Garcetti",
    "Eric Trump",
    "Filemon Vela",
    "Gary Peters",
    "Gavin Newsom",
    "Gretchen Whitmer",
    "Gwen Moore",
    "Hillary Clinton",
    "Ilhan Omar",
    "Jamie Harrison",
    "Joaquin Castro",
    "Joe Gruters",
    "John Carney",
    "John Kerry",
    "John Lynch",
    "John McCain",
    "John Kasich",
    "Jon Meacham",
    "Josh Holt",
    "Karen Pence",
    "Keisha Lance Bottoms",
    "Kellyanne Conway",
    "Kirsten Gillibrand",
    "Kristi Noem",
    "Lindsey Graham",
    "Lisa Blunt Rochester",
    "Lori Lightfoot",
    "Madison Cawthorn",
    "Malcolm Kenyatta",
    "Mandela Barnes",
    "Maria Cardona",
    "Mark Meadows",
    "Martha McSally",
    "Matt Gaetz",
    "Melania Trump",
    "Melvin Carter",
    "Michelle Lujan Grisham",
    "Mike Bloomberg",
    "Mike Pompeo",
    "Mitch McConnell",
    "Muriel Bowser",
    "Nancy Pelosi",
    "Ned Lamont",
    "Nikki Fried",
    "Nikki Haley",
    "Pete Buttigieg",
    "Phil Murphy",
    "Pramila Jayapal",
    "Rand Paul",
    "Raphael Warnock",
    "Ronna McDaniel",
    "Ron DeSantis",
    "Ron Kind",
    "Ron Klain",
    "Seth Moulton",
    "Stacey Abrams",
    "Steve Sisolak",
    "Tammy Baldwin",
    "Tammy Duckworth",
    "Ted Kaufman",
    "Ted Lieu",
    "Thom Tillis",
    "Tim Ryan",
    "Tim Scott",
    "Tom Carper",
    "Tom Perez",
    "Tom Steyer",
    "Tulsi Gabbard",
    "Val Demings",
    "Veronica Escobar",
    "Yvanna Cancela",
    "Zoe Lofgren",
]

# %% Gráfico con la categoría Otros
df = (
    df_speeches_2[df_speeches_2["speaker"].isin(politicos)]
    .groupby(["week", "speaker_2"])
    .apply(lambda x: x.index.nunique(), include_groups=False)
    .reset_index(name="speeches")
    .sort_values("week")
)
df_pivot = df.pivot(index="week", columns="speaker_2", values="speeches").fillna(0)
df_pivot = df_pivot[
    [
        "Joe Biden",
        "Kamala Harris",
        "Bernie Sanders",
        "Donald Trump",
        "Mike Pence",
        "Otros",
    ]
]
df_pivot.index = df_pivot.index.strftime("%b %d")
stacked_bar_plot(
    df=df_pivot,
    save_path="img/discursos_candidatos_por_semana_2.png",
    color=["#1f77b4", "#4e9cd5", "#8fbadd", "#d62728", "#e96a6a", "#949494"],
    plot_title="Discursos por Candidato en el Año 2020",
    xlabel="Semana",
    ylabel="Cantidad de Discursos",
    ylim_top=44,
)

# %% Ejecuto location_analysis.py
execute_location_analysis(df=df_speeches)
