import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from circlify import circlify
import numpy as np
from wordcloud import WordCloud
import networkx as nx


def circle_packing_plot(ds: pd.Series, save_path: str, scale: int = 2, threshold: float = 0.15):
    """
    Plot a circle packing plot from a series of counts.

    Args:
        ds: The series to plot.
        save_path: The path to save the plot.
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
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.axis("off")

    lim = max(
        max(
            abs(circle.x * scale) + circle.r * scale,
            abs(circle.y * scale) + circle.r * scale,
        )
        for circle in circles
    )
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)

    color_palette = sns.color_palette(palette="tab10", n_colors=20)
    for i, circle in enumerate(circles):
        x, y, r = circle
        x = x * scale
        y = y * scale
        r = r * scale

        color_idx = i % len(color_palette)
        random_color = color_palette[color_idx]
        ax.add_patch(
            plt.Circle(xy=(x, y), radius=r, alpha=0.5, linewidth=2, fill=True, color=random_color)
        )
        font_size = max(8, min(20, r * 40))
        speaker = speaker_names[i].replace(" ", "\n")
        if len(speaker) > 12 and r < 0.1:
            speaker = speaker[:12] + "..."

        ax.text(x=x, y=y, s=speaker, ha="center", va="center", fontsize=font_size)

        # Add count below the text for circles bigger than the threshold
        if r > threshold:
            count = count_values[i]
            ax.text(
                x=x,
                y=y - font_size / 100,
                s=f"({count})",
                ha="center",
                va="center",
                fontsize=font_size * 0.8,
                alpha=0.8,
            )

        fig.tight_layout()
        fig.savefig(fname=save_path, dpi=300, bbox_inches='tight')
        plt.close(fig)


def stacked_bar_plot(df: pd.DataFrame, save_path: str, color: list, plot_title: str, xlabel: str, ylabel: str, ylim_top: int, ylim_bottom: int = 0):
    fig, ax = plt.subplots(figsize=(14, 6))
    df.plot(
        kind='bar',
        stacked=True,
        # Tiene que estar en el mismo orden que las columnas
        color=color,
        ax=ax,
        width=0.8
    )
    fig.suptitle(t=plot_title, fontweight='bold')
    ax.set_xlabel(xlabel)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=30)
    ax.set_ylabel(ylabel)
    ax.set_ylim(bottom=ylim_bottom, top=ylim_top)
    ax.set_yticks(np.arange(ylim_bottom, ylim_top, 2))
    ax.legend(title=None, loc='upper center', bbox_to_anchor=(0.5, 1.1), ncol=len(df.columns), frameon=False)
    ax.yaxis.grid(visible=True, linestyle='--', alpha=0.6)
    ax.set_axisbelow(True)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    fig.tight_layout()
    fig.savefig(fname=save_path, dpi=300, bbox_inches='tight')
    plt.close(fig)


def word_cloud_plot(df: pd.DataFrame, save_path: str, plot_title: str, colormap, stopwords: set, max_words: int, text: str, speaker: str):
    fig, ax = plt.subplots(nrows=1, ncols=len(df.index), figsize=(30, 6))
    for i, row in df.iterrows():
        wc = WordCloud(
            width=400,
            height=400,
            background_color='white',
            colormap=colormap,
            stopwords=stopwords,
            max_words=max_words
        ).generate(row[text])
        ax[i].imshow(wc, interpolation='bilinear')
        ax[i].axis('off')
        ax[i].set_title(row[speaker], fontsize=30)
    fig.suptitle(t=plot_title, fontweight='bold', x=0.45)
    fig.tight_layout()
    fig.subplots_adjust(right=0.9, left=0, bottom=0, top=0.85)
    fig.savefig(fname=save_path, dpi=300, bbox_inches='tight')
    plt.close(fig)


def directed_graph_plot(df: pd.DataFrame, save_path: str, plot_title: str, colors: dict):
    graph = nx.from_pandas_adjacency(df=df, create_using=nx.DiGraph)
    edge_weights = nx.get_edge_attributes(G=graph, name='weight')
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_xlim(left=-1.1, right=1.2)
    pos = nx.circular_layout(G=graph)
    nx.draw_networkx_nodes(
        G=graph,
        pos=pos,
        node_size=2000,
        node_color=[colors[node] for node in graph.nodes()]
    )
    nx.draw_networkx_labels(
        G=graph,
        pos=pos,
        font_size=12,
        font_weight='bold'
    )
    for source, target in graph.edges():
        rad = 0.2
        nx.draw_networkx_edges(
            G=graph,
            pos=pos,
            arrows=True,
            edgelist=[(source, target)],
            arrowstyle="->",
            connectionstyle=f"arc3,rad={rad}",
            arrowsize=20,
            node_size=2000 if source != target else 2000 * 0.3,
            edge_color=colors[source]
        )
        edge_label = {(source, target): edge_weights[(source, target)]}
        nx.draw_networkx_edge_labels(
            G=graph,
            pos=pos,
            edge_labels=edge_label,
            connectionstyle=f'arc3,rad={rad}',
            font_size=12,
            font_color=colors[source],
            font_weight='bold',
            bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=0.3),
            rotate=False,
            node_size=2000 if source != target else 2000 * 0.3
        )
    fig.suptitle(t=plot_title, fontweight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    fig.tight_layout()
    fig.savefig(fname=save_path, dpi=300)
    plt.close(fig)
