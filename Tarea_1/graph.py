# %%
import re

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import start_research

from ddelpo.clean_data import clean_text

# %%
df_speeches = pd.read_csv(
    filepath_or_buffer=r"data/us_2020_election_speeches.csv", sep=","
)
# %%
# %%
top5_speakers = list(df_speeches["speaker"].value_counts().head(5).index)
df_speeches_top5 = df_speeches[df_speeches["speaker"].isin(top5_speakers)].copy()


# %%
def get_speaker_text_from_transcript(speaker: str, text: str) -> str:
    regex = rf"(\w*\s*{speaker.split(' ')[1]}): (.+)\n(.+)"
    matches = re.findall(regex, text)
    if matches:
        return "\n".join([match[2] for match in matches])
    else:
        return text


df_speeches_top5["clean_text"] = df_speeches_top5.apply(
    lambda x: get_speaker_text_from_transcript(x["speaker"], x["text"]), axis=1
)
print(
    df_speeches_top5[df_speeches_top5["speaker"] == "Kamala Harris"].iloc[3][
        "clean_text"
    ]
)
# %%
df_speeches_top5["clean_text"] = clean_text(
    df=df_speeches_top5, column_name="clean_text"
)
top5_speakers_texts = df_speeches_top5.groupby("speaker").clean_text.aggregate(" ".join)
top5_speakers_texts


# %%
adj_matrix = pd.DataFrame(data=0, index=top5_speakers, columns=top5_speakers, dtype=int)
for i, speaker in enumerate(top5_speakers):
    for j, other_speaker in enumerate(top5_speakers):
        # Count how many times the other speaker's name appears in this speaker's text
        speaker_text: str = top5_speakers_texts[speaker]
        adj_matrix.loc[speaker, other_speaker] = speaker_text.count(
            other_speaker.split(" ")[1].lower()
        )

adj_matrix
# %%
graph = nx.from_pandas_adjacency(adj_matrix, create_using=nx.DiGraph)

# %%
colores_por_candidato = {
    "Bernie Sanders": "#8fbadd",
    "Donald Trump": "#d62728",
    "Joe Biden": "#1f77b4",
    "Kamala Harris": "#4e9cd5",
    "Mike Pence": "#e96a6a",
}

edge_weights = nx.get_edge_attributes(graph, "weight")
pos = nx.shell_layout(graph)
nx.draw(
    graph,
    pos=pos,
    with_labels=True,
    node_size=1000,
    font_size=10,
    node_color=[colores_por_candidato[node] for node in graph.nodes()],
)
nx.draw_networkx_edge_labels(graph, pos=pos, edge_labels=edge_weights, font_size=10)
plt.savefig("img/graph.png", dpi=300)
