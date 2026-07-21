from __future__ import annotations

from itertools import combinations

import pytest

from verify import (
    construct_tight_sparse_graph,
    has_packing_subgraph_exact,
    is_sparse,
    is_tau_maximal_exact,
)


Edge = tuple[int, int]


def complete_edges(order: int) -> tuple[Edge, ...]:
    return tuple(combinations(range(order), 2))


def edges_from_mask(all_edges: tuple[Edge, ...], mask: int) -> tuple[Edge, ...]:
    return tuple(edge for index, edge in enumerate(all_edges) if mask & (1 << index))


def test_exact_tree_packing_and_sparsity_agree_exhaustively() -> None:
    # The r=2 case also contains every four-vertex graph by adding an isolate;
    # (r, n)=(3, 6) is the smallest case of the paper's open k=2 range.
    for order, packing_count in ((5, 2), (6, 3)):
        all_edges = complete_edges(order)
        for mask in range(1 << len(all_edges)):
            edges = edges_from_mask(all_edges, mask)

            assert is_sparse(order, edges, packing_count) is (
                not has_packing_subgraph_exact(order, edges, packing_count)
            )


def test_nontrivial_three_tree_packing_uses_all_seven_vertices() -> None:
    spanning_trees = (
        {(0, 6), (1, 4), (1, 5), (2, 3), (2, 4), (3, 6)},
        {(0, 2), (1, 6), (2, 5), (3, 4), (3, 5), (4, 6)},
        {(0, 3), (0, 4), (1, 3), (2, 6), (4, 5), (5, 6)},
    )
    edges = tuple(sorted(set().union(*spanning_trees)))

    assert all(len(tree) == 6 for tree in spanning_trees)
    assert len(edges) == 18
    assert (
        max(
            sum(u in vertices and v in vertices for u, v in edges)
            for vertices in map(set, combinations(range(7), 6))
        )
        < 15
    )
    assert has_packing_subgraph_exact(7, edges, packing_count=3)
    assert not is_sparse(7, edges, packing_count=3)


def test_smallest_k2_tau_maximal_graphs_are_exactly_k6_minus_one_edge() -> None:
    order = 6
    all_edges = complete_edges(order)
    maximal_graphs: list[tuple[Edge, ...]] = []

    for mask in range(1 << len(all_edges)):
        edges = edges_from_mask(all_edges, mask)
        if is_tau_maximal_exact(order, edges, k=2):
            maximal_graphs.append(edges)

    assert len(maximal_graphs) == len(all_edges)
    assert {len(edges) for edges in maximal_graphs} == {14}
    assert {
        next(edge for edge in all_edges if edge not in edges)
        for edges in maximal_graphs
    } == set(all_edges)


def test_k2_graph_missing_two_edges_is_not_tau_maximal() -> None:
    edges = tuple(edge for edge in complete_edges(6) if edge not in {(0, 1), (2, 3)})

    assert not is_tau_maximal_exact(6, edges, k=2)


def test_explicit_tight_construction_meets_the_claimed_rank() -> None:
    for packing_count in range(2, 5):
        for order in range(2 * packing_count, 2 * packing_count + 4):
            edges = construct_tight_sparse_graph(order, packing_count)

            assert len(edges) == packing_count * order - (packing_count + 1)
            assert is_sparse(order, edges, packing_count)

            missing_edges = set(complete_edges(order)) - set(edges)
            assert missing_edges
            assert all(
                not is_sparse(order, (*edges, edge), packing_count)
                for edge in missing_edges
            )


@pytest.mark.parametrize(
    ("call", "message"),
    (
        (lambda: is_sparse(4.0, (), 2), "order must be a plain integer"),
        (lambda: is_sparse(4, ((0.5, 1),), 2), "endpoints must be plain integers"),
        (lambda: is_sparse(4, (), 2.0), "packing_count must be a plain integer"),
        (
            lambda: has_packing_subgraph_exact(True, (), 2),
            "order must be a plain integer",
        ),
        (lambda: is_tau_maximal_exact(4, (), k=1.0), "k must be a plain integer"),
        (
            lambda: construct_tight_sparse_graph(4, packing_count=False),
            "packing_count must be a plain integer",
        ),
    ),
)
def test_public_api_rejects_noninteger_graph_data(call, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        call()
