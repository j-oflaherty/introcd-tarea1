# Importamos los módulos a utilizar
import pandas as pd
import matplotlib.pyplot as plt
from ddelpo.clean_data import clean_text, search_punctuation, list_of_tuples
from wordcloud import WordCloud, STOPWORDS
import locale


# DataFrame con todos los discursos
df_speeches = pd.read_csv(r'data/us_2020_election_speeches.csv', sep=',')

# Tipos de datos
print(df_speeches.dtypes)
df_speeches['date'] = pd.to_datetime(df_speeches['date'], format='%b %d, %Y')

# Datos faltantes
print(df_speeches.isna().sum())

# Cantidad de discursos por tipo
print(df_speeches.groupby('type').size().sort_values(ascending=False))

# Cantidad de discursos por ubicación
# La mayoría fueron virtuales por el COVID-19
print(df_speeches.groupby('location').size().sort_values(ascending=False))

# TODO: Analice la cantidad de discursos por candidato
n_speeches = df_speeches.groupby('speaker').size().sort_values(ascending=False)

# Quiero ver todos los oradores
print(df_speeches.speaker.unique())

# Veo que hay discursos donde hay más de un candidato en la columna 'speaker'
# Como veo que están los nombres separados por ',' quiero ver si es significativa la cantidad de registros
print(len(df_speeches[df_speeches['speaker'].str.contains(',', na=False)]))

# También veo otros registros donde no se identifica al candidato
print(len(df_speeches[df_speeches['speaker'] == 'Multiple Speakers']))
print(len(df_speeches[df_speeches['speaker'] == 'Democratic Candidates']))
print(len(df_speeches[df_speeches['speaker'] == '???']))

# Hay 36 registros en los que no es posible determinar el orador por la columna 'speaker'
# Voy a generar un DataFrame cuya estructura sea una fila por intervención de cada orador
# Es decir que un discurso va a tener más de una fila
df_speeches_2 = df_speeches.copy()

# Elimino lo que está entre [] como [crosstalk...], [inaudible...], etc.
df_speeches_2['text'] = df_speeches_2['text'].str.replace(r'\[.*?\]', '', regex=True)

# Este comercial en particular me rompe el index 79 donde quiero separar las intervenciones
df_speeches_2['text'] = df_speeches_2['text'].str.replace('Commercial: (48:14)\r\n', '')

# Elimino el patrón ': (mm:ss)'
df_speeches_2['text'] = df_speeches_2['text'].str.replace(r': \(\d{2}:\d{2}\)', '', regex=True)

# Elimino el patrón ': (hh:mm:ss)'
df_speeches_2['text'] = df_speeches_2['text'].str.replace(r': \(\d{2}:\d{2}\:\d{2}\)', '', regex=True)

# Convierto la columna en una lista donde cada elemento es una intervención de un orador
df_speeches_2['text'] = df_speeches_2['text'].str.split(r'\r\n(?:\xa0\r\n)?', regex=True)

# Convierto la lista en una lista de tuplas donde cada tupla tiene el par orador-discurso
df_speeches_2['text'] = df_speeches_2['text'].apply(list_of_tuples)

# Con explode hago que cada elemento de la lista (cada tupla) sea una fila
df_speeches_2 = df_speeches_2.explode('text')

# Sobreescribo los valores de speaker y text con los valores de cada tupla
df_speeches_2[['speaker', 'text']] = pd.DataFrame(
    df_speeches_2['text'].tolist(),
    index=df_speeches_2.index
)

# Chequeo con los index que la cantidad de discursos sigue siendo la misma
print(len(df_speeches_2.index.unique()))

# Quiero ver los candidatos que me quedaron
df_speeches_2.to_excel(r'data/speeches.xlsx')

# Top 5 candidatos con más discursos
top_5 = list(n_speeches.head(5).index)

# Quiero ver como aparecen los 5 principales candidatos
print(df_speeches_2[df_speeches_2['speaker'].str.contains('Trump', na=False)]['speaker'].unique())
print(df_speeches_2[df_speeches_2['speaker'].str.contains('Biden', na=False)]['speaker'].unique())
print(df_speeches_2[df_speeches_2['speaker'].str.contains('Pence', na=False)]['speaker'].unique())
print(df_speeches_2[df_speeches_2['speaker'].str.contains('Harris', na=False)]['speaker'].unique())
print(df_speeches_2[df_speeches_2['speaker'].str.contains('Sanders', na=False)]['speaker'].unique())

# Homogeneizar nombres
names = {
    'President Trump': 'Donald Trump',
    'President Donald J. Trump': 'Donald Trump',
    'President Donald Trump': 'Donald Trump',
    'Donald J. Trump': 'Donald Trump',
    'Trump': 'Donald Trump',
    'Vice President Joe Biden': 'Joe Biden',
    'VIce President Biden': 'Joe Biden',
    'Joe Biden ': 'Joe Biden',
    'Vice President Mike Pence': 'Mike Pence',
    'Vice President Mike Pence ': 'Mike Pence',
    'Kamala Harris ': 'Kamala Harris',
    'Senator Kamala Harris': 'Kamala Harris',
    'Senator Harris': 'Kamala Harris',
    'Senator Bernie Sanders': 'Bernie Sanders',
    'Sanders': 'Bernie Sanders'
}
df_speeches_2['speaker'] = df_speeches_2['speaker'].map(names).fillna(df_speeches_2['speaker'])


# Me quedo con las intervenciones del top 5
df_speeches_top_5 = df_speeches_2[df_speeches_2['speaker'].isin(top_5)].copy()

# Datos faltantes
print(df_speeches_top_5.isna().sum())

# Asignar partido politico
parties = {
    'Joe Biden': 'Partido Demócrata',
    'Kamala Harris': 'Partido Demócrata',
    'Bernie Sanders': 'Partido Demócrata',
    'Donald Trump': 'Partido Republicano',
    'Mike Pence': 'Partido Republicano'
}
df_speeches_top_5['party'] = df_speeches_top_5['speaker'].map(parties)

# Para chequear escala temporal
print(df_speeches_top_5['date'].min())
print(df_speeches_top_5['date'].max())
df_speeches_top_5['week'] = df_speeches_top_5['date'].dt.to_period('W').apply(lambda r: r.start_time)

# Establecer el locale a español
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

# TODO: Visualización de los discursos de cada candidato a lo largo del tiempo
df = df_speeches_top_5.groupby(['week', 'speaker']).apply(lambda x: x.index.nunique(), include_groups=False).reset_index(name='speeches').sort_values('week')
df_pivot = df.pivot(index='week', columns='speaker', values='speeches').fillna(0)
df_pivot.index = df_pivot.index.strftime('%b %d')
# Tiene que estar en el mismo orden que las columnas
colores_por_candidato = {
    'Bernie Sanders': '#8fbadd',
    'Donald Trump': '#d62728',
    'Joe Biden': '#1f77b4',
    'Kamala Harris': '#4e9cd5',
    'Mike Pence': '#e96a6a'
}
plt.figure()
df_pivot.plot(
    kind='bar',
    stacked=True,
    color=[colores_por_candidato[col] for col in df_pivot.columns],
    figsize=(14, 6)
)
plt.xlabel('Semana')
plt.ylabel('Discursos')
plt.title('Discursos por Candidato en el Año 2020')
plt.xticks(rotation=30)
plt.legend(title='Candidato')
plt.tight_layout()
plt.ioff()
plt.savefig('img/discursos_candidatos_por_semana.png', dpi=300, bbox_inches='tight')
plt.close()

# Visualización de los discursos de cada partido a lo largo del tiempo
df = df_speeches_top_5.groupby(['week', 'party']).apply(lambda x: x.index.nunique(), include_groups=False).reset_index(name='speeches').sort_values('week')
df_pivot = df.pivot(index='week', columns='party', values='speeches').fillna(0)
df_pivot.index = df_pivot.index.strftime('%b %d')
plt.figure()
df_pivot.plot(
    kind='bar',
    stacked=True,
    color=['#1f77b4', '#d62728'],
    figsize=(14, 6)
)
plt.xlabel('Semana')
plt.ylabel('Discursos')
plt.title('Discursos por Partido Político en el Año 2020')
plt.xticks(rotation=30)
plt.legend(title='Partido')
plt.tight_layout()
plt.ioff()
plt.savefig('img/discursos_partidos_por_semana.png', dpi=300, bbox_inches='tight')
plt.close()

# Busco los signos de puntuacion que existen para despues agregarlos a la funcion clean_text
print(search_punctuation(df_speeches_top_5, 'text'))

# TODO: Creamos una nueva columna CleanText a partir de text
df_speeches_top_5['clean_text'] = clean_text(df_speeches_top_5, 'text')

# Convierte parrafos en listas 'palabra1 palabra2 palabra3' -> ['palabra1', 'palabra2', 'palabra3']
df_speeches_top_5['word_list'] = df_speeches_top_5['clean_text'].str.split()

# Veamos la nueva columna creada: notar que a la derecha tenemos una lista: [palabra1, palabra2, palabra3]
print(df_speeches_top_5[['clean_text', 'word_list']])

# TODO: Realice una visualización que permita comparar las palabras más frecuentes de cada uno de los cinco candidatos/as.
#   Encuentra algún problema en los resultados?
df = df_speeches_top_5.groupby('speaker')['clean_text'].apply(lambda palabras: ' '.join(palabras)).reset_index()
fig, axes = plt.subplots(nrows=1, ncols=5, figsize=(22, 5))
for i, row in df.iterrows():
    wc = WordCloud(
        width=400,
        height=400,
        background_color='white',
        # Para eliminar palabras comunes del idioma que no aportan (agrego otras que no trae el módulo worldcloud)
        stopwords=STOPWORDS.update(['s', 're', 'don', 'didn', 'know', 'will', 'going', 'need', 't', 'people', 'think', 'want', 'well', 'let', 'said', 'thank'])
    ).generate(row['clean_text'])
    axes[i].imshow(wc, interpolation='bilinear')
    axes[i].axis('off')
    axes[i].set_title(row['speaker'], fontsize=14)
plt.tight_layout()
plt.ioff()
plt.savefig('img/wordcloud_por_candidato.png', dpi=300, bbox_inches='tight')
plt.close()

# El problema en los resultados son las palabras comunes
# Esas palabras quitan el foco de otras palabras que pueden indicar los tópicos que cada candidato considera más relevantes

# TODO: Busque los candidatos/as con mayor cantidad de palabras.
df_speeches_top_5['n_words'] = df_speeches_top_5['word_list'].apply(lambda palabras: len(palabras))
print(df_speeches_top_5.groupby('speaker')['n_words'].sum().sort_values(ascending=False))

# Formas de mencionar a los candidatos
menciones = {
    'Joe Biden': [r'\bjoe biden\b', r'\bbiden\b', r'\bvice president biden\b', r'\bvice president joe biden\b'],
    'Donald Trump': [r'\bdonald trump\b', r'\btrump\b', r'\bpresident trump\b', r'\bpresident donald\b', r'\bdonald\b'],
    'Mike Pence': [r'\bmike pence\b', r'\bpence\b', r'\bvice president pence\b'],
    'Bernie Sanders': [r'\bbernie sanders\b', r'\bsanders\b'],
    'Kamala Harris': [r'\bkamala harris\b', r'\bharris\b', r'\bsenator harris\b', r'\bkamala\b']
}

# TODO: Construya una matriz de 5x5, donde cada fila y columna corresponden a un candiato/a,
#   y la entrada (i,j) contiene la cantidad de veces que el candiato/a “i” menciona al candiato/a “j”.
# mentions_matrix = ...

# Opcional: Genere un grafo dirigido con esa matriz de adyacencia para visualizar las menciones.
# Puede ser util la biblioteca networkx