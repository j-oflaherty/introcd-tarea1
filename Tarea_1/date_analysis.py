# %%
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import start_research

INCLUDE_OTHERS = False
# %%
df = pd.read_csv("data/us_2020_election_speeches.csv")
df["date"] = pd.to_datetime(df["date"])
df["speaker"] = df["speaker"].map(
    lambda x: list(map(str.strip, x.split(","))) if isinstance(x, str) else x
)
df = df.explode("speaker")

# %%
top5_speakers = df["speaker"].value_counts().head(5).index.tolist()
if INCLUDE_OTHERS:
    df["speaker"] = df["speaker"].apply(
        lambda x: "Otros" if x not in top5_speakers else x
    )
else:
    df = df[df["speaker"].isin(top5_speakers)]
# %%
df["date"].dt.month.value_counts()
# %%
df["week"] = df["date"].dt.to_period("W").apply(lambda r: r.start_time)
df["week"].value_counts()
# %%
df_speeches_per_week = (
    df.groupby(["week", "speaker"])
    .size()
    .reset_index(name="speeches")
    .sort_values("week")
)
df_pivot = df_speeches_per_week.pivot(
    index="week", columns="speaker", values="speeches"
).fillna(0)
df_pivot.index = df_pivot.index.strftime("%b %d")
# %%
colores_por_candidato = {
    "Bernie Sanders": "#8fbadd",
    "Donald Trump": "#d62728",
    "Mike Pence": "#e96a6a",
    "Joe Biden": "#1f77b4",
    "Kamala Harris": "#4e9cd5",
    "Otros": "#949494",
}

df_long = df_pivot.reset_index().melt(
    id_vars="week", var_name="speaker", value_name="speeches"
)
fig, ax = plt.subplots(figsize=(10, 6))
df_pivot.plot(
    kind="bar",
    stacked=True,
    ax=ax,
    color=colores_por_candidato,
    width=0.8,
)
plt.grid(axis="y")
plt.xlabel("Semana", fontsize=16)
plt.ylabel("Cantidad de discursos", fontsize=16)
plt.title("Discursos por semana", fontsize=18)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.legend(title="Candidato", fontsize=14, title_fontsize=16)
plt.tight_layout()
plt.savefig(
    "img/speeches_por_semana.png"
    if INCLUDE_OTHERS
    else "img/speeches_por_semana_top5.png",
    dpi=300,
    bbox_inches="tight",
)
plt.show()
plt.close()

# %%
