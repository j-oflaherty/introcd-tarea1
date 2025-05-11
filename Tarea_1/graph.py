# %%
import re

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import start_research

from ddelpo.clean_data import clean_text

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

# %%
df_speeches = pd.read_csv(
    filepath_or_buffer=r"data/us_2020_election_speeches.csv", sep=","
)


# %%
def get_speakers_from_transcript(text):
    regex = r"\n([\w\s*]+): \([\d\:]+\)"
    matches = re.findall(regex, text)
    return set([match.strip() for match in matches if "Speaker" not in match])


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
    df=df_speeches_top5,
    column_name="clean_text" if "clean_text" in df_speeches_top5.columns else "text",
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
graph.is_directed()
# %%
graph.get_edge_data("Donald Trump", "Kamala Harris")

# %%
colores_por_candidato = {
    "Bernie Sanders": "#8fbadd",
    "Donald Trump": "#d62728",
    "Joe Biden": "#1f77b4",
    "Kamala Harris": "#4e9cd5",
    "Mike Pence": "#e96a6a",
}

edge_weights = nx.get_edge_attributes(graph, "weight")
plt.figure(figsize=(8, 6))
plt.xlim(-1.1, 1.2)
pos = nx.circular_layout(graph)
node_size = 2000
nx.draw_networkx_nodes(
    graph,
    pos=pos,
    node_size=node_size,
    node_color=[colores_por_candidato[node] for node in graph.nodes()],
)
nx.draw_networkx_labels(
    graph,
    pos=pos,
    font_size=12,
    font_weight="bold",  # horizontalalignment="center",
    # verticalalignment="baseline",
)

for source, target in graph.edges():
    rad = 0.2
    nx.draw_networkx_edges(
        graph,
        pos,
        arrows=True,
        edgelist=[(source, target)],
        arrowstyle="->",
        connectionstyle=f"arc3,rad={rad}",
        arrowsize=20,
        node_size=node_size if source != target else node_size * 0.3,
        edge_color=colores_por_candidato[source],
    )
    # Add edge labels with weights
    edge_label = {(source, target): edge_weights[(source, target)]}
    nx.draw_networkx_edge_labels(
        graph,
        pos,
        edge_labels=edge_label,
        connectionstyle=f"arc3,rad={rad}",
        font_size=10,
        font_color=colores_por_candidato[source],
        font_weight="bold",
        bbox=dict(facecolor="white", alpha=0.7, edgecolor="none", pad=0.3),
        rotate=False,
        node_size=node_size if source != target else node_size * 0.3,
    )

plt.tight_layout()
plt.savefig("img/graph.png", dpi=300)

# %%
