# %%
import re
from collections import Counter
from pprint import pprint

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import start_research

from Tarea_1.utils.plots import cicrle_packing_plot

df = pd.read_csv("data/us_2020_election_speeches.csv")

raw_speakers = df["speaker"].unique()
print("Total number of speakers:", len(raw_speakers))
print(raw_speakers)
print("\n\n")

missing_speakers = df[df["speaker"].isnull() | (df["speaker"] == "???")]
print(
    "Speaches missing speaker:",
    len(missing_speakers),
)
print(missing_speakers["title"].to_list())
print("\n")
print("Speech with speaker ???:", df[df["speaker"] == "???"]["title"].iloc[0])


def get_speakers(text):
    regex = r"\n([\w\s*]+): \([\d\:]+\)"
    matches = re.findall(regex, text)
    return set([match.strip() for match in matches if "Speaker" not in match])


print("Analysing `Multiple Speakers`")
counter: Counter[str] = Counter()
print("Speech title\t\t\t\t\t\t\tApproximate Speaker count")
for i, row in df[df["speaker"] == "Multiple Speakers"].iterrows():
    speakers = get_speakers(row["text"])
    counter.update(speakers)
    print(f"{row['title']}\t\t{len(speakers)}")


print("Top 10 appearences")
pprint(counter.most_common(10))
df[df["speaker"] == "Multiple Speakers"]["title"].to_list()

# Remove invalid speakers
df = df[~df["speaker"].isin(["Multiple Speakers", "???"])]


def get_speaker_text_from_transcript(speaker: str, text: str) -> str:
    regex = rf"({speaker}): (.+)\n(.+)"
    matches = re.findall(regex, text)
    return "\n".join([match[2] for match in matches]) if matches else None


df_multiple_speakers_mask = df["speaker"].str.split(",").str.len() > 1
df_multiple_speakers = df[df_multiple_speakers_mask].copy()
df_multiple_speakers["speaker"] = df_multiple_speakers["speaker"].map(
    lambda x: list(map(str.strip, x.split(","))) if isinstance(x, str) else x
)
df_multiple_speakers = df_multiple_speakers.explode("speaker")
df_multiple_speakers["text"] = df_multiple_speakers.apply(
    lambda row: get_speaker_text_from_transcript(row["speaker"], row["text"]),
    axis=1,
)
df_multiple_speakers = df_multiple_speakers.dropna()
df = pd.concat([df[~df_multiple_speakers_mask], df_multiple_speakers])


cicrle_packing_plot(df["speaker"].value_counts(), scale=2)
plt.savefig("img/speaker_count_visualization.png", dpi=300)
plt.show()
