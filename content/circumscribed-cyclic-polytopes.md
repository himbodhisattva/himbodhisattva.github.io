---
title: "every cyclic polytope C_d(d+3) is circumscribable"
description: "A failed counterexample hunt produced an exact, dimension-independent proof that every cyclic polytope with d+3 vertices has a realization circumscribed about a sphere."
section: "proofs"
---

# every cyclic polytope `C_d(d+3)` is circumscribable

**Theorem, not counterexample.** This is an exact proof draft. It has not been peer reviewed.

A cyclic polytope is the convex hull of points on the moment curve

```text
t -> (t, t^2, ..., t^d).
```

A polytope is circumscribable if it has a realization whose facets all touch one sphere, with the sphere inside every supporting halfspace.

Here is the result that fell out of trying to find a counterexample:

> **Theorem.** For every `d >= 2`, the cyclic polytope `C_d(d+3)` is circumscribable. In fact, the equally spaced realization at `t = 0, 1, ..., d+2` has a projective image with every facet tangent to one sphere.

If correct, this answers [Questions 3.13 and 6.2 in Doolittle, Labbé, Lange, Sinn, Spreer, and Ziegler](https://arxiv.org/abs/1910.05241). They reported that they could not find the required quadric for `C_6(9)`. That made dimension six look like a plausible place for circumscribability to fail. It was instead the first case where the hidden general construction became visible.

## the proof idea

Write `m = d + 1` and use the equally spaced moment-curve vertices. Every facet omits three vertex indices `a < b < c`. Gale's rule for cyclic polytopes says that the two gaps

```text
u = b - a,   v = c - b
```

must both be odd.

The supporting hyperplanes can be represented by polynomials. Take the facets omitting three consecutive vertices as a basis. In this basis, the facet omitting `a, b, c` is a positive multiple of a simple tent-shaped vector: it rises linearly to one peak and then falls linearly again.

That reduces the geometry to one matrix. Define a symmetric matrix `G`, constant along each diagonal, by

```text
G(i,i)     = 0
G(i,i+1)   = 3
G(i,i+r)   = 4r(-1)^(r+1)   for r >= 2.
```

A finite-sum identity shows that every odd-gap tent vector `h` satisfies

```text
h^T G h = 0.
```

So all the facet hyperplanes lie on one quadric. The same matrix has exactly one negative eigenvalue: after alternating the coordinate signs, it becomes `-4` times a distance matrix plus a path-adjacency correction, and it is positive on the codimension-one subspace where the coordinates sum to zero. Its trace is zero, forcing the final eigenvalue to be negative.

Set `Q = -G`. Then `Q` has the one-positive-direction signature needed for a sphere in projective geometry. One final sign calculation shows that the inward-facing facet hyperplanes all lie on the same half of the null cone. That matters: it says the tangent sphere is inside every facet halfspace, rather than merely touching the supporting hyperplanes with inconsistent orientations.

A projective change of coordinates turns that quadric into the ordinary unit sphere. This proves the theorem.

## what it does and does not settle

The proof is dimension-independent. Exact arithmetic checks reproduce every identity for `2 <= d <= 12`; those checks are regression tests, not the reason the theorem holds.

Doolittle and collaborators noted that a negative example in this family would refute a broader conjecture of Grünbaum. This result closes that particular route to a counterexample. It does **not** prove Grünbaum's conjecture for all polytopes with few vertices.

I do not know whether the argument is new. A targeted literature search during the project did not find a posted proof, but that is not a priority claim. The cautious status is: exact proof draft, checked computationally in finite dimensions, not peer reviewed.
