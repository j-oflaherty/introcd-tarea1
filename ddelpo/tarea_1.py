# Importamos los modulos a utilizar
import pandas as pd
import matplotlib.pyplot as plt
from ddelpo.clean_data import clean_text, search_punctuation, clean_names
from wordcloud import WordCloud, STOPWORDS

# DataFrame con todos los discursos
df_speeches = pd.read_csv(r'data/us_2020_election_speeches.csv', sep=',')

# Tipos de datos
print(df_speeches.dtypes)
df_speeches['date'] = pd.to_datetime(df_speeches['date'], format='%b %d, %Y')

# Datos faltantes
print(df_speeches.isna().sum())

# Cantidad de discursos por tipo
print(df_speeches.groupby('type').size().sort_values(ascending=False))

# TODO: Analice la cantidad de discursos por candidato
print(df_speeches.groupby('speaker').size().sort_values(ascending=False))

# Tome los 5 candidatos con más discursos
top_5 = list(df_speeches.groupby('speaker').size().sort_values(ascending=False).head(5).index)
df_speeches_top_5 = df_speeches[df_speeches['speaker'].isin(top_5)].copy()

# Asignar partido politico
parties = {
    'Joe Biden': 'Democratic',
    'Kamala Harris': 'Democratic',
    'Bernie Sanders': 'Democratic',
    'Donald Trump': 'Republican',
    'Mike Pence': 'Republican'
}
df_speeches_top_5['party'] = df_speeches_top_5['speaker'].map(parties)

# Para chequear escala temporal
print(df_speeches_top_5['date'].min())
print(df_speeches_top_5['date'].max())
df_speeches_top_5['week'] = df_speeches_top_5['date'].dt.to_period('W').apply(lambda r: r.start_time)

# TODO: Visualización de los discursos de cada candidato a lo largo del tiempo
df = df_speeches_top_5.groupby(['week', 'speaker']).size().reset_index(name='speeches').sort_values('week')
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
plt.xlabel('Week')
plt.ylabel('Speeches')
plt.title('Campaing speeches per candidate')
plt.xticks(rotation=30)
plt.legend(title='Candidate')
plt.tight_layout()
plt.ioff()
plt.savefig('img/discursos_candidatos_por_semana.png', dpi=300, bbox_inches='tight')
plt.close()

# Visualización de los discursos de cada partido a lo largo del tiempo
df = df_speeches_top_5.groupby(['week', 'party']).size().reset_index(name='speeches').sort_values('week')
df_pivot = df.pivot(index='week', columns='party', values='speeches').fillna(0)
df_pivot.index = df_pivot.index.strftime('%b %d')
plt.figure()
df_pivot.plot(
    kind='bar',
    stacked=True,
    color=['#1f77b4', '#d62728'],
    figsize=(14, 6)
)
plt.xlabel('Week')
plt.ylabel('Speeches')
plt.title('Campaing speeches per party')
plt.xticks(rotation=30)
plt.legend(title='Party')
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

# Elimino los nombres de los candidatos
df_speeches_top_5['clean_text_no_names'] = clean_names(df_speeches_top_5, 'clean_text')

# TODO: Realice una visualización que permita comparar las palabras más frecuentes de cada uno de los cinco candidatos/as.
#   Encuentra algún problema en los resultados?
df = df_speeches_top_5.groupby('speaker')['clean_text_no_names'].apply(lambda palabras: ' '.join(palabras)).reset_index()
fig, axes = plt.subplots(nrows=1, ncols=5, figsize=(22, 5))
for i, row in df.iterrows():
    wc = WordCloud(
        width=400,
        height=400,
        background_color='white',
        # Para eliminar palabras comunes del idioma que no aportan (agrego otras que no trae el modulo worldcloud)
        stopwords=STOPWORDS.update(['s', 're', 'don t', 'didn t'])
    ).generate(row['clean_text_no_names'])
    axes[i].imshow(wc, interpolation='bilinear')
    axes[i].axis('off')
    axes[i].set_title(row['speaker'], fontsize=14)
plt.tight_layout()
plt.ioff()
plt.savefig('img/wordcloud_por_candidato.png', dpi=300, bbox_inches='tight')
plt.close()
