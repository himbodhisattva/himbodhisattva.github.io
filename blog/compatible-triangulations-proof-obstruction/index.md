# compatible triangulations: a theorem and an obstruction

> **Authorship disclaimer:** This proof was written primarily by GPT-5.6-sol.

**Status: partial theorem plus an obstruction to one proof strategy. The full conjecture remains open.**

Take two planar point sets with the same number of points and the same number of points on their convex hulls. Match the hull points in cyclic order. The compatible-triangulation conjecture asks whether that hull matching can always be extended to all the points so that one abstract triangulation can be drawn without crossings on both sets. This is [Conjecture 1.1 in Hong Duc Bui's paper](https://arxiv.org/abs/2508.04602).

A large exact counterexample search kept finding compatible triangulations, including cases with only one surviving matching. Mining those failures produced a clean sufficient condition.

## sufficient theorem

Suppose the two point sets already carry corresponding drawings of the same spanning, 2-connected planar graph `H`, with the prescribed hull cycle on the outside and the same oriented boundary cycle for each corresponding face.

Each bounded face of `H` is a simple polygon. For a face `F`, let `D_P(F)` be the set of vertex pairs that can be joined by a diagonal lying inside that face in the first drawing. Define `D_Q(F)` the same way in the second drawing.

> **Face-visibility theorem.** If, separately in every nontriangular face, either `D_P(F)` is contained in `D_Q(F)` or `D_Q(F)` is contained in `D_P(F)`, then `H` extends to compatible triangulations of both point sets.

The direction of containment may change from face to face.

The proof is short. In each face, triangulate the drawing whose visible-diagonal set is contained in the other one. Every chosen diagonal is also valid in the other drawing. Whether two diagonals cross inside a simple polygon depends only on whether their endpoints alternate around its boundary, so the transported diagonals remain noncrossing. Do this independently in every face and unite the results with `H`.

This is a theorem, not a guess from the computations. It is a face-by-face version of the polygon visibility argument in Bui's Proposition 6.2. I make no novelty claim for that underlying idea.

## why the failed search kept surviving

Call an edge of a point set unavoidable when no other point-pair segment crosses it. Every triangulation contains every unavoidable edge.

For a proposed matching `f`, combine the unavoidable edges on the first set with the pullback of the unavoidable edges on the second. In the hardest low-overlap examples from the search, this common core was 2-connected, and the corresponding faces satisfied the visibility theorem. The apparently mysterious lone compatible triangulation was therefore forced by a smaller visible-diagonal set sitting inside a larger one.

That suggested a tempting route to the whole conjecture: perhaps one could always choose `f` so this unavoidable common core was 2-connected and facewise visibility-dominating.

## obstruction to this route, not to the conjecture

An exact `n = 16` example kills that proposed lemma. In the search archive it is labeled `L0/R1`, hull shift zero.

The example has twelve interior vertices. In the first point set's unavoidable graph, four of those vertices are isolated (`5, 6, 10, 13`). In the second point set's unavoidable graph, only three interior vertices have degree at least two (`7, 8, 14`).

No bijection can match all four isolated vertices to those three high-degree vertices. Therefore at least one isolated vertex on the first side must receive degree at most one from the second side. Its degree in the combined unavoidable graph is still at most one, so that graph cannot be 2-connected.

This is a tiny Hall-style counting certificate, and it applies to **every** interior bijection for that prescribed hull map. Yet the exact global solver found at least four compatible mappings for the same pair.

So the conclusion is precise:

- the face-visibility condition is a valid sufficient theorem;
- it explains the selected hard survivors from the failed counterexample hunt;
- the unavoidable-edge core cannot always supply the required 2-connected scaffold; and
- the 16-point example obstructs this proof route, not compatible triangulations themselves.

A proof of the full conjecture along these lines would need a principled way to add a common scaffold beyond the unavoidable edges. Choosing that scaffold from an already known compatible triangulation would merely restate the problem.

The theorem and the degree-count obstruction have exact proofs. The broader computational search and its implementation have not been peer reviewed, and neither result is a disproof of Bui's conjecture.
