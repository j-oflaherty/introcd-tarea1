import matplotlib.pyplot as plt
import pandas as pd
from geopandas import read_file


def execute(df: pd.DataFrame):
    df["date"] = pd.to_datetime(df["date"])
    df["speaker"] = df["speaker"].map(
        lambda x: list(map(str.strip, x.split(","))) if isinstance(x, str) else x
    )
    df = df.explode("speaker")
    top5_speakers = df["speaker"].value_counts().head(5).index.tolist()

    df.head()

    for location in df["location"].unique():
        print(location)

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
    print("State Value counts: ", df["state"].value_counts())

    news_channels = ["ABC", "NBC", "Fox News", "Virtual", "CNN"]
    df["news_channel"] = df["location"].apply(
        lambda x: x if x in news_channels else None
    )

    df_with_states = df[df["state"].notna()].copy()
    df_top5_speakers = df_with_states[
        df_with_states["speaker"].isin(top5_speakers)
    ].copy()

    candidate_affiliation = {
        "Joe Biden": "Partido Demócrata",
        "Donald Trump": "Partido Republicano",
        "Kamala Harris": "Partido Demócrata",
        "Mike Pence": "Partido Republicano",
        "Bernie Sanders": "Partido Demócrata",
    }

    df_top5_speakers["candidate_affiliation"] = df_top5_speakers["speaker"].map(
        lambda x: candidate_affiliation[x]
    )

    all_states = read_file("maps/states")
    all_states = all_states[all_states["iso_a2"] == "US"][
        ~all_states["name"].isin(["Alaska", "Hawaii"])
    ]
    df_party_speech_by_state = (
        df_top5_speakers.groupby(["candidate_affiliation", "state"])
        .size()
        .unstack()
        .fillna(0)
    )

    def get_winner(row):
        if row.get("Partido Demócrata", 0) > row.get("Partido Republicano", 0):
            return "Partido Demócrata"
        elif row.get("Partido Republicano", 0) > row.get("Partido Demócrata", 0):
            return "Partido Republicano"
        else:
            return "Empate"

    winner_by_state = df_party_speech_by_state.T.apply(get_winner, axis=1)
    all_states["winner"] = all_states["name"].map(winner_by_state)

    dem_counts = (
        df_party_speech_by_state.loc["Partido Demócrata"]
        if "Partido Demócrata" in df_party_speech_by_state.index
        else pd.Series()
    )
    rep_counts = (
        df_party_speech_by_state.loc["Partido Republicano"]
        if "Partido Republicano" in df_party_speech_by_state.index
        else pd.Series()
    )

    all_states["dem_count"] = all_states["name"].map(dem_counts).fillna(0).astype(int)
    all_states["rep_count"] = all_states["name"].map(rep_counts).fillna(0).astype(int)

    color_map = {
        "Partido Demócrata": "#1f77b4",
        "Partido Republicano": "red",
        "Empate": "gray",
    }

    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(20, 10))
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

    for _, row in all_states.dropna(subset=["winner"]).iterrows():
        if row["geometry"].centroid.is_valid:
            x, y = row["geometry"].centroid.x, row["geometry"].centroid.y
            dx, dy = offsets.get(row["name"], (0, 0))
            label = f"{row['dem_count']}/{row['rep_count']}"
            plt.text(
                x + dx,
                y + dy,
                label,
                ha="center",
                va="center",
                fontsize=20,
                color="black",
                weight="bold",
            )

    plt.title(
        "Estados Coloreados por el Partido con más Discursos\n(Demócrata/Republicano)",
        fontsize=24,
        fontweight="bold",
    )
    plt.axis("off")
    plt.savefig("img/states_map.png", dpi=300)
    plt.close(fig)

    print("News channel value count: ", df["news_channel"].value_counts())
    df_top5_speakers_news_channel = df[
        (df["news_channel"].notnull()) & (df["speaker"].isin(top5_speakers))
    ].copy()
    df_top5_speakers_news_channel["candidate_affiliation"] = (
        df_top5_speakers_news_channel["speaker"].map(lambda x: candidate_affiliation[x])
    )
    fig, ax = plt.subplots(figsize=(10, 5))
    df_top5_speakers_news_channel.groupby(
        ["news_channel", "candidate_affiliation"]
    ).size().unstack().fillna(0).plot(
        kind="bar",
        stacked=True,
        color=list(color_map.values()),
        ax=ax,
    )
    fig.suptitle(
        t="Distribución de Discursos por Partido y Canal de Noticias",
        fontweight="bold",
    )
    ax.set_xlabel("Canal de Noticias")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
    ax.set_ylabel("Cantidad de Discursos")
    ax.legend(
        title=None,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.05),
        ncol=2,
        frameon=False,
    )
    ax.yaxis.grid(visible=True, linestyle="--", alpha=0.6)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(fname="img/news_channel_dist.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    df_top5_speakers = df[df["speaker"].isin(top5_speakers)].copy()
    print("Virtual ", df_top5_speakers["news_channel"].notnull().sum())
    print("State ", df_top5_speakers["state"].notnull().sum())

    print(
        "Missing to clasify",
        df_top5_speakers[
            (df_top5_speakers["news_channel"].isnull())
            & (df_top5_speakers["state"].isnull())
        ],
    )
