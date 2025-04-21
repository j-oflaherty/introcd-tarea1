# %%
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import start_research

# %%
df = pd.read_csv("data/us_2020_election_speeches.csv")
# %%
df.head()
# %%
df["type"].value_counts()

# %%
plt.figure(figsize=(12, 5))
ax = sns.countplot(x="type", data=df)

labels = [item.get_text() for item in ax.get_xticklabels()]
labels = [label.replace(" ", "\n") for label in labels]
ax.set_xticklabels(labels)

plt.xticks(ha="center", fontsize=12)
plt.yticks(fontsize=12)
plt.xlabel("Type", fontsize=14)
plt.ylabel("Count", fontsize=14)
plt.title("Count of Speeches by Type", fontsize=16)
plt.tight_layout()
# %%
speech_count_by_speaker = df["speaker"].value_counts()
speech_count_by_speaker.head()
# %%
len(df["speaker"].unique())
# %%
speech_count_by_speaker[speech_count_by_speaker == 1].size
print(
    f"Speakers with 1 speech: {speech_count_by_speaker[speech_count_by_speaker == 1].size}"
)
# %%
speakers_with_at_least_2_speeches = df[
    df["speaker"].isin(
        df["speaker"].value_counts()[df["speaker"].value_counts() > 1].index
    )
]
speakers_with_at_least_2_speeches.head()

# %%
plt.figure(figsize=(12, 5))
ax = sns.countplot(x="speaker", data=speakers_with_at_least_2_speeches)

labels = [item.get_text() for item in ax.get_xticklabels()]
labels = [label.replace(" ", "\n") for label in labels]
ax.set_xticklabels(labels)

plt.xticks(ha="center", fontsize=12)
plt.yticks(fontsize=12)
plt.xlabel("Speaker", fontsize=14)
plt.ylabel("Count", fontsize=14)
plt.title("Count of Speeches by Speaker", fontsize=16)
plt.tight_layout()

# %%
for sp in df["speaker"].unique():
    print(sp)

# %%
print(df[df["speaker"] == "???"].iloc[0].text)
# %%
# df[~df['speaker'].notna()]
# # %%
# df['speaker'] = df['speaker'].map(lambda x: x.split(',') if isinstance(x, str) else x)
# # %%
# df.explode('speaker')


# %%
def get_speeches_per_speaker(
    df: pd.DataFrame, include_shared: bool = True, exclude: list[str] | None = []
):
    """
    Get the number of speeches per speaker.
    If include_shared is True, it will include speeches shared by multiple speakers.

    Args:
        df: The dataframe to analyze. It must have a 'speaker' column.
        include_shared: Whether to include speeches shared by multiple speakers.
            If True, it'll parse the 'speaker' column as a list of speakers and add it
            to each speakers count.

    Returns:
        A series with the number of speeches per speaker.
    """
    if include_shared:
        df = pd.DataFrame(
            df["speaker"].map(
                lambda x: list(map(str.strip, x.split(",")))
                if isinstance(x, str)
                else x
            )
        )
        df = df.explode("speaker")

    if exclude:
        df = df[~df["speaker"].isin(exclude)]

    return df["speaker"].value_counts()


# %%
counts = get_speeches_per_speaker(
    df, exclude=["???", "Democratic Candidates", "Multiple Speakers"]
)

# %%
import numpy as np
from circlify import circlify

sorted_counts = counts.sort_values(ascending=False)
speaker_names = sorted_counts.index.tolist()
count_values = sorted_counts.tolist()

circles = circlify(count_values)
circles = circles[::-1]
fig, ax = plt.subplots(figsize=(10, 10))
scale = 2

ax.axis("off")

lim = max(
    max(
        abs(circle.x * scale) + circle.r * scale,
        abs(circle.y * scale) + circle.r * scale,
    )
    for circle in circles
)
plt.xlim(-lim, lim)
plt.ylim(-lim, lim)

color_palette = sns.color_palette("tab10", 20)
for i, circle in enumerate(circles):
    x, y, r = circle
    x = x * scale
    y = y * scale
    r = r * scale

    color_idx = i % len(color_palette)
    random_color = color_palette[color_idx]
    ax.add_patch(
        plt.Circle((x, y), r, alpha=0.5, linewidth=2, fill=True, color=random_color)
    )

    font_size = max(8, min(12, r * 20))
    speaker = speaker_names[i].replace(" ", "\n")
    if len(speaker) > 12 and r < 0.1:
        speaker = speaker[:12] + "..."

    plt.text(x, y, speaker, ha="center", va="center", fontsize=font_size)
# %%
