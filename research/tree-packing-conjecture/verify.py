"""Exact finite checks for the Wang--Tian tree-packing conjecture.

The direct checker uses the Nash-Williams--Tutte partition criterion.  The
sparsity checker is deliberately separate so exhaustive tests can compare the
two formulations rather than testing one implementation against itself.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from functools import lru_cache
from itertools import combinations


Edge = tuple[int, int]


def _validate_order(order: int) -> None:
    if type(order) is not int:
        raise ValueError("order must be a plain integer")
    if order < 2:
        raise ValueError("order must be at least 2")


def _normalize_edges(order: int, edges: Iterable[Edge]) -> tuple[Edge, ...]:
    _validate_order(order)

    normalized: set[Edge] = set()
    for u, v in edges:
        if type(u) is not int or type(v) is not int:
            raise ValueError("edge endpoints must be plain integers")
        if u == v:
            raise ValueError("loops are not allowed")
        if not 0 <= u < order or not 0 <= v < order:
            raise ValueError("edge endpoint is outside the vertex set")
        edge = (u, v) if u < v else (v, u)
        if edge in normalized:
            raise ValueError("parallel or duplicate edges are not allowed")
        normalized.add(edge)
    return tuple(sorted(normalized))


def _validate_packing_count(packing_count: int) -> None:
    if type(packing_count) is not int:
        raise ValueError("packing_count must be a plain integer")
    if packing_count < 2:
        raise ValueError("packing_count must be at least 2")


def is_sparse(order: int, edges: Iterable[Edge], packing_count: int) -> bool:
    """Return whether ``edges`` is ``(r, r+1)``-sparse for ``r=packing_count``."""

    _validate_packing_count(packing_count)
    normalized = _normalize_edges(order, edges)
    return _is_sparse_normalized(order, normalized, packing_count)


@lru_cache(maxsize=None)
def _is_sparse_normalized(
    order: int, edges: tuple[Edge, ...], packing_count: int
) -> bool:
    vertices = range(order)
    for subset_size in range(2, order + 1):
        edge_bound = packing_count * subset_size - (packing_count + 1)
        for subset_tuple in combinations(vertices, subset_size):
            subset = set(subset_tuple)
            induced_edge_count = sum(u in subset and v in subset for u, v in edges)
            if induced_edge_count > edge_bound:
                return False
    return True


def _set_partitions(vertices: tuple[int, ...]) -> Iterator[tuple[tuple[int, ...], ...]]:
    """Yield every set partition once, with blocks in canonical creation order."""

    blocks: list[list[int]] = [[vertices[0]]]

    def visit(index: int) -> Iterator[tuple[tuple[int, ...], ...]]:
        if index == len(vertices):
            yield tuple(tuple(block) for block in blocks)
            return

        vertex = vertices[index]
        for block in blocks:
            block.append(vertex)
            yield from visit(index + 1)
            block.pop()

        blocks.append([vertex])
        yield from visit(index + 1)
        blocks.pop()

    yield from visit(1)


@lru_cache(maxsize=None)
def _packs_spanning_trees(
    vertices: tuple[int, ...], edges: tuple[Edge, ...], packing_count: int
) -> bool:
    if len(edges) < packing_count * (len(vertices) - 1):
        return False

    for partition in _set_partitions(vertices):
        if len(partition) == 1:
            continue
        block_of = {
            vertex: block_index
            for block_index, block in enumerate(partition)
            for vertex in block
        }
        crossing_edges = sum(block_of[u] != block_of[v] for u, v in edges)
        if crossing_edges < packing_count * (len(partition) - 1):
            return False
    return True


def has_packing_subgraph_exact(
    order: int, edges: Iterable[Edge], packing_count: int
) -> bool:
    """Check exactly whether some subgraph packs ``packing_count`` spanning trees."""

    _validate_packing_count(packing_count)
    normalized = _normalize_edges(order, edges)
    return _has_packing_subgraph_normalized(order, normalized, packing_count)


@lru_cache(maxsize=None)
def _has_packing_subgraph_normalized(
    order: int, edges: tuple[Edge, ...], packing_count: int
) -> bool:
    # A simple graph on s > 1 vertices can contain r spanning trees only if
    # binom(s, 2) >= r(s - 1), equivalently s >= 2r.
    for subset_size in range(2 * packing_count, order + 1):
        required_edges = packing_count * (subset_size - 1)
        for subset_tuple in combinations(range(order), subset_size):
            subset = set(subset_tuple)
            induced_edges = tuple(
                edge for edge in edges if edge[0] in subset and edge[1] in subset
            )
            if len(induced_edges) < required_edges:
                continue
            if _packs_spanning_trees(subset_tuple, induced_edges, packing_count):
                return True
    return False


def is_tau_maximal_exact(order: int, edges: Iterable[Edge], k: int) -> bool:
    """Check the paper's definition of ``tau_k``-maximality directly."""

    if type(k) is not int:
        raise ValueError("k must be a plain integer")
    if k < 1:
        raise ValueError("k must be at least 1")
    normalized = _normalize_edges(order, edges)
    packing_count = k + 1
    if _has_packing_subgraph_normalized(order, normalized, packing_count):
        return False

    edge_set = set(normalized)
    for edge in combinations(range(order), 2):
        if edge in edge_set:
            continue
        augmented = tuple(sorted((*normalized, edge)))
        if not _has_packing_subgraph_normalized(order, augmented, packing_count):
            return False
    return True


def construct_tight_sparse_graph(order: int, packing_count: int) -> tuple[Edge, ...]:
    """Construct a simple ``(r, r+1)``-tight graph for every ``n >= 2r``."""

    _validate_order(order)
    _validate_packing_count(packing_count)
    if order < 2 * packing_count:
        raise ValueError("order must be at least twice packing_count")

    base_order = 2 * packing_count
    edges = [edge for edge in combinations(range(base_order), 2) if edge != (0, 1)]
    for vertex in range(base_order, order):
        edges.extend((neighbor, vertex) for neighbor in range(packing_count))
    return tuple(edges)
