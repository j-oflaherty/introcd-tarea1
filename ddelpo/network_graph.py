# Importamos los módulos a utilizar
import itertools as it
import networkx as nx


def draw_labeled_multigraph(G, attr_name, ax=None):
    """
    The length of connectionstyle must be at least that of a maximum number of edges
    between a pair of nodes. This number is maximum one-sided connections
    for the directed graph and maximum total connections for the undirected graph.
    """
    # Works with arc3 and angle3 connectionstyles
    connectionstyle = [f"arc3,rad={r}" for r in it.accumulate([0.15] * 4)]
    # connectionstyle = [f"angle3,angleA={r}" for r in it.accumulate([30] * 4)]

    pos = nx.shell_layout(G)
    nx.draw_networkx_nodes(G, pos, ax=ax)
    nx.draw_networkx_labels(G, pos, ax=ax)
    nx.draw_networkx_edges(
        G,
        pos,
        edge_color="grey",
        connectionstyle=connectionstyle,
        ax=ax
    )

    labels = {
        tuple(edge): f"{attr_name}={attrs[attr_name]}"
        for *edge, attrs in G.edges(keys=True, data=True)
    }
    nx.draw_networkx_edge_labels(
        G,
        pos,
        labels,
        connectionstyle=connectionstyle,
        label_pos=0.3,
        font_color="blue",
        bbox={"alpha": 0},
        ax=ax,
    )
