import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from circlify import circlify


def cicrle_packing_plot(ds: pd.Series, scale: int = 2, threshold: float = 0.15):
    """
    Plot a circle packing plot from a series of counts.

    Args:
        ds: The series to plot.
        scale: The scale of the plot.
        threshold: The threshold for showing count values in circles.

    Returns:
        A plot of the circle packing plot.
    """
    sorted_counts = ds.sort_values(ascending=False)
    speaker_names = sorted_counts.index.tolist()
    count_values = sorted_counts.tolist()

    circles = circlify(count_values)
    circles = circles[::-1]
    _, ax = plt.subplots(figsize=(10, 10))
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
        font_size = max(8, min(20, r * 40))
        speaker = speaker_names[i].replace(" ", "\n")
        if len(speaker) > 12 and r < 0.1:
            speaker = speaker[:12] + "..."

        plt.text(x, y, speaker, ha="center", va="center", fontsize=font_size)

        # Add count below the text for circles bigger than the threshold
        if r > threshold:
            count = count_values[i]
            plt.text(
                x,
                y - font_size / 100,
                f"({count})",
                ha="center",
                va="center",
                fontsize=font_size * 0.8,
                alpha=0.8,
            )
