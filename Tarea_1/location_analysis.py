# %%
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import pandas as pd
import start_research

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
df = pd.read_csv("data/us_2020_election_speeches.csv")
df["date"] = pd.to_datetime(df["date"])
df["speaker"] = df["speaker"].map(
    lambda x: list(map(str.strip, x.split(","))) if isinstance(x, str) else x
)
df = df.explode("speaker")
# %%
top5_speakers = df["speaker"].value_counts().head(5).index.tolist()

# %%
df.head()

# %%
for location in df["location"].unique():
    print(location)


# %%
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
    "wyoming",
]


def get_state(location):
    if not isinstance(location, str):
        return None
    location = location.split(",")
    if len(location) == 2:
        return location[1].strip()
    if location[0].lower() in us_states_list:
        return location[0]
    else:
        return None


df["state"] = df["location"].apply(get_state)
# %%
df["state"].value_counts()
# %%
df.head()
# %%
news_channels = ["ABC", "NBC", "Fox News", "Virtual", "CNN"]
df["news_channel"] = df["location"].apply(lambda x: x if x in news_channels else None)
# %%
(
    df["news_channel"].value_counts().sum()
    + df["location"].isna().sum()
    + df["state"].value_counts().sum()
)

# %%
(
    df["news_channel"].value_counts().sum()
    + df["location"].isna().sum()
    + df["state"].value_counts().sum(),
    df["location"].value_counts().sum(),
)
# %%
df_with_states = df[df["state"].notna()]
print(df_with_states["speaker"].value_counts()[:15])

# %%
df_top5_speakers = df_with_states[df_with_states["speaker"].isin(top5_speakers)]
speeches_by_state = (
    df_top5_speakers.groupby(["state", "speaker"]).size().unstack().fillna(0)
)
speeches_by_state.plot(kind="bar", stacked=True)

# %%

# %%
df_with_states.groupby(["speaker", "state"]).size().unstack().fillna(0)

# %%
candidate_affiliation = {
    "Joe Biden": "Democrata",
    "Donald Trump": "Republicano",
    "Kamala Harris": "Democrata",
    "Mike Pence": "Republicano",
    "Bernie Sanders": "Democrata",
}

df_top5_speakers["candidate_affiliation"] = df_top5_speakers["speaker"].map(
    lambda x: candidate_affiliation[x]
)
df_top5_speakers.head()
# %%

# %%
from geopandas import read_file

all_states = read_file("maps/states")
all_states = all_states[all_states["iso_a2"] == "US"][
    ~all_states["name"].isin(["Alaska", "Hawaii"])
]
# %%
df_party_speech_by_state = (
    df_top5_speakers.groupby(["candidate_affiliation", "state"])
    .size()
    .unstack()
    .fillna(0)
)
# %%


def get_winner(row):
    if row.get("Democrata", 0) > row.get("Republicano", 0):
        return "Democrata"
    elif row.get("Republicano", 0) > row.get("Democrata", 0):
        return "Republicano"
    else:
        return "Empate"


winner_by_state = df_party_speech_by_state.T.apply(get_winner, axis=1)
all_states["winner"] = all_states["name"].map(winner_by_state)

dem_counts = (
    df_party_speech_by_state.loc["Democrata"]
    if "Democrata" in df_party_speech_by_state.index
    else pd.Series()
)
rep_counts = (
    df_party_speech_by_state.loc["Republicano"]
    if "Republicano" in df_party_speech_by_state.index
    else pd.Series()
)

# Map to all_states
all_states["dem_count"] = all_states["name"].map(dem_counts).fillna(0).astype(int)
all_states["rep_count"] = all_states["name"].map(rep_counts).fillna(0).astype(int)


color_map = {"Democrata": "#1f77b4", "Republicano": "red", "Empate": "gray"}

fig, ax = plt.subplots(1, 1, figsize=(20, 10))
all_states.boundary.plot(ax=ax, color="black", linewidth=0.5)
all_states.dropna(subset=["winner"]).plot(
    ax=ax,
    color=all_states.dropna(subset=["winner"])["winner"].map(color_map),
    edgecolor="black",
    linewidth=0.5,
)

offsets = {
    "New Jersey": (0.3, -0.3),
    "New Hampshire": (0.3, -0.4),
    "Vermont": (0.0, 0.3),
    "Michigan": (0.5, -0.3),
    "Florida": (0.5, -0.3),
    "Delaware": (0.5, -0.3),
}

for idx, row in all_states.dropna(subset=["winner"]).iterrows():
    if row["geometry"].centroid.is_valid:
        x, y = row["geometry"].centroid.x, row["geometry"].centroid.y
        # Apply offset if state is in offsets dict
        dx, dy = offsets.get(row["name"], (0, 0))
        label = f"{row['dem_count']}/{row['rep_count']}"
        text = plt.text(
            x + dx,
            y + dy,
            label,
            ha="center",
            va="center",
            fontsize=20,
            color="black",
            weight="bold",
        )
        # text.set_path_effects(
        #     [
        #         path_effects.Stroke(linewidth=2, foreground="white"),
        #         path_effects.Normal(),
        #     ]
        # )

plt.title(
    "Estados coloreados por el partido con más discursos\n(Demócrata/Republicano)",
    fontsize=24,
)
plt.axis("off")
plt.savefig("img/states_map.png", dpi=300)
plt.show()

# %%
(~df["state"].isna()).sum(), (~df["news_channel"].isna()).sum()
# %%
df["news_channel"].value_counts()
# %%
df_top5_speakers_news_channel = df[
    (df["news_channel"].notnull()) & (df["speaker"].isin(top5_speakers))
].copy()
df_top5_speakers_news_channel["candidate_affiliation"] = df_top5_speakers_news_channel[
    "speaker"
].map(lambda x: candidate_affiliation[x])
# %%
df_top5_speakers_news_channel.groupby(
    ["news_channel", "candidate_affiliation"]
).size().unstack().fillna(0).plot(
    kind="bar", stacked=True, color=list(color_map.values())
)
plt.grid(which="major", axis="y", alpha=0.5)
plt.title("Distribución de discursos por partido y canal de noticias")
plt.legend(title="Partido", title_fontsize=12, fontsize=11)
plt.xticks(rotation=0, ha="center", fontsize=11)
plt.xlabel("Canal de noticias", fontsize=12)
plt.ylabel("Número de discursos", fontsize=12)
plt.yticks(fontsize=11)
plt.tight_layout()
plt.savefig("img/news_channel_dist.png", dpi=300)
plt.show()

# %%
df_top5_speakers.head()
# %%
df_top5_speakers.head()
# %%
df_top5_speakers = df[df["speaker"].isin(top5_speakers)].copy()
df_top5_speakers["candidate_affiliation"] = df_top5_speakers["speaker"].map(
    lambda x: candidate_affiliation[x]
)
# %%
print("Virtual ", df_top5_speakers["news_channel"].notnull().sum())
print("State ", df_top5_speakers["state"].notnull().sum())
# %%
df_top5_speakers[
    (df_top5_speakers["news_channel"].isnull()) & (df_top5_speakers["state"].isnull())
].count()
