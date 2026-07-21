# A short proof of Wang--Tian Conjecture 1

## Status

As of 2026-07-20, the argument below proves Conjecture 1 of Qinglin Wang and
Yingzhi Tian's June 2026 preprint. The reduction is proved self-containedly and
also checked against the standard sparsity-matroid theorem, but the note has not
been submitted or peer reviewed. This is a proof route, not a counterexample.

The paper is
[arXiv:2606.28198](https://arxiv.org/abs/2606.28198), *Extremal graphs with no
subgraph admitting \(k+1\) edge-disjoint spanning trees*. It defines

\[
\bar\tau(G)=\max\{\tau(H):H\subseteq G\}
\]

and calls \(G\) \(\tau_k\)-maximal when \(\bar\tau(G)\le k\), while
\(\bar\tau(G+e)\ge k+1\) for every missing edge \(e\). Its Conjecture 1 says
that every such graph on \(n\ge2k+2\) vertices has

\[
|E(G)|=(k+1)(n-1)-1.
\]

## Scoop check

An authenticated X **Latest** search on 2026-07-20 used the calendar filter
`since:2026-07-19`, which contains the requested last-24-hour window. These
queries returned no relevant mathematical posts:

- `"2606.28198"`
- `("tau_k" OR "τ_k" OR "tau k") (maximal OR "tree packing")`
- `("Wang" AND "Tian") ("spanning trees" OR "tree packing")`
- `("spanning tree packing" OR "spanning-tree-packing") conjecture`
- `"Extremal graphs with no subgraph admitting"`
- `("Qinglin Wang" OR "Yingzhi Tian") ("spanning tree" OR graph)`

The broad author-name query produced unrelated posts about people named Wang
Tian, not graph theory. Web searches for the arXiv identifier or exact title
together with `sparsity matroid`, and for `tau_k-maximal` together with
`matroid` or `conjecture`, found the paper and automated summaries but no proof
or disproof. This is a reasonable freshness check, not a guarantee of novelty.

## Step 1: identify the independence system

Put

\[
r=k+1.
\]

The paper assumes \(k\ge1\), so \(r\ge2\). For a nonempty edge set \(F\), let
\(V(F)\) be the vertices incident with \(F\). Recall that \(F\) is
\((r,r+1)\)-sparse when

\[
|F'|\le r|V(F')|-(r+1)
\tag{1}
\]

for every nonempty \(F'\subseteq F\).

**Lemma.** A finite simple graph \(G\) satisfies \(\bar\tau(G)<r\) if and only
if \(E(G)\) is \((r,r+1)\)-sparse.

**Forward direction.** Suppose (1) fails for a nonempty \(F\subseteq E(G)\).
Integrality gives

\[
|F|\ge r|V(F)|-r=r(|V(F)|-1).
\]

Apply Corollary 2.2 of Wang--Tian to the graph \((V(F),F)\). It contains a
subgraph packing \(r\) edge-disjoint spanning trees, contradicting
\(\bar\tau(G)<r\).

**Reverse direction.** If a subgraph \(H\subseteq G\) packs \(r\) edge-disjoint
spanning trees, the union \(F\) of any \(r\) of them has

\[
|F|=r(|V(H)|-1)=r|V(F)|-r,
\]

which exceeds the right side of (1) by one. Thus \(E(G)\) is not sparse.
Here \(r\ge2\), so under the paper's standard tree-packing convention a witness
has at least two vertices and the union is incident with every vertex of \(H\).

This also explains why the paper's global density bound is one edge short of a
tree packing: the hereditary version of that bound is exactly a standard
sparsity condition.

## Step 2: prove the matroid exchange axiom

The needed matroid statement has a short self-contained proof in this special
case. This avoids any dependence on a source that states its basis theorem only
for sufficiently large ground sets.

Fix the ground set \(E(K_n)\), and write

\[
f(X)=r|X|-(r+1),\qquad
i_A(X)=|A\cap E(K_n[X])|.
\]

For \(|X|\ge2\), the edge-subset definition (1) is equivalent to
\(i_A(X)\le f(X)\). If the edge set induced by \(X\) is empty, this inequality
is automatic because \(f(X)\ge r-1\ge1\); otherwise one direction applies (1)
to that induced edge set. The other applies the induced inequality to
\(X=V(F')\) for each nonempty
\(F'\subseteq A\). Call \(X\) **\(A\)-tight** when \(|X|\ge2\) and
\(i_A(X)=f(X)\).

First observe that if \(A\) is sparse and a missing edge \(e=uv\) makes
\(A+e\) nonsparse, then some \(A\)-tight set contains \(u,v\). Indeed, a
violating edge set must contain \(e\). If its incident vertex set is \(X\),
write it as \(F'\). Integrality and sparsity of \(A\) give

\[
f(X)\le |F'\setminus\{e\}|\le i_A(X)\le f(X),
\]

so every inequality is equality.

Next, two \(A\)-tight sets \(X,Y\) whose intersection has at least two
vertices can be uncrossed. The induced-edge counts satisfy

\[
i_A(X)+i_A(Y)
=i_A(X\cup Y)+i_A(X\cap Y)
 - |A\cap E(X\setminus Y,Y\setminus X)|
\le i_A(X\cup Y)+i_A(X\cap Y).
\]

Since \(f\) is modular on vertex sets,

\[
f(X)+f(Y)=f(X\cup Y)+f(X\cap Y).
\]

Both the union and the intersection have at least two vertices, so sparsity
applies to them. Consequently,

\[
f(X\cup Y)+f(X\cap Y)
=i_A(X)+i_A(Y)
\le i_A(X\cup Y)+i_A(X\cap Y)
\le f(X\cup Y)+f(X\cap Y).
\]

Every inequality is equality. In particular, \(X\cup Y\) and \(X\cap Y\)
are tight, and there is no \(A\)-edge between \(X\setminus Y\) and
\(Y\setminus X\). It follows that two distinct inclusion-maximal
\(A\)-tight vertex sets intersect in at most one vertex. Their induced edge
sets are therefore disjoint: an edge in both would have two endpoints in the
intersection.

Now let \(A,B\) be sparse with \(|A|<|B|\). Suppose, for contradiction, that
no edge of \(B\setminus A\) can augment \(A\). Every such edge lies in an
\(A\)-tight set by the first observation, and hence in an inclusion-maximal
one. Let \(X_1,\ldots,X_t\) be the distinct maximal tight sets that cover
these edges. Their induced edge sets are disjoint. Since \(B\) is sparse, for
each \(i\),

\[
|B[X_i]|\le f(X_i)=|A[X_i]|,
\]

and therefore

\[
|(B\setminus A)[X_i]|\le |(A\setminus B)[X_i]|.
\]

Every edge of \(B\setminus A\) occurs in exactly one of these induced edge
sets, while the corresponding \(A\setminus B\) edge sets are disjoint subsets
of \(A\setminus B\). Summing yields

\[
|B\setminus A|
\le \sum_i |(A\setminus B)[X_i]|
\le |A\setminus B|.
\]

Thus \(|B|-|A|=|B\setminus A|-|A\setminus B|\le0\), a contradiction. The
sparse sets are hereditary, contain the empty set, and now satisfy augmentation,
so they are the independent sets of a matroid for every \(n\).

The singleton convention is used exactly where necessary: tightness and the
induced inequalities are invoked only for sets of at least two vertices. The
parameter condition \(r\ge2\) ensures a single simple edge is sparse because
\(1\le f(\{u,v\})=r-1\).

## Step 3: compare with the standard sparsity matroid theorem

For integers \(a,b\) with \(0\le b\le2a-1\), the
\((a,b)\)-sparse edge sets of a simple host graph are the independent sets of
its sparsity matroid. Sources spelling out the definition and range include:

- [Lee and Streinu](https://arxiv.org/abs/math/0702129), *Pebble Game
  Algorithms and Sparse Graphs*, Discrete Mathematics 308 (2008),
  [doi:10.1016/j.disc.2007.07.104](https://doi.org/10.1016/j.disc.2007.07.104),
  which treats integer parameters throughout \(0\le b<2a\);
- [Ito, Tanigawa, and Yoshida](https://arxiv.org/abs/1103.2581), which defines
  sparsity using every nonempty edge subset and states the matroid property for
  a host graph;
- [Iwata, Kamiyama, Katoh, Kijima, and Okamoto](https://arxiv.org/abs/1403.7272),
  which uses the simple-graph formulation and the range
  \(0\le b\le2a-1\);
- [Streinu and Theran](https://arxiv.org/abs/0711.3013), Proposition 1 and
  Theorem A, which give the corresponding general \(d\)-uniform sparsity
  matroid and a linear representation throughout \(0\le b\le da-1\), for
  sufficiently large ground-set order. The self-contained exchange proof above
  is what covers every order needed here.

Here \(a=r\) and \(b=r+1\). Since \(r\ge2\),

\[
0\le r+1\le2r-1.
\]

Thus the standard theorem independently confirms the exchange proof. There is
no hidden singleton obstruction: the definition quantifies over **nonempty
edge sets**, whose incident vertex set has at least two vertices. There is also
no multigraph mismatch. The cited host-graph formulation applies directly to
simple \(K_n\); equivalently, it is the restriction of the uniform-hypergraph
sparsity matroid to one copy of each pair. Matroid restriction preserves the
matroid axioms.

By the lemma, a \(\tau_k\)-maximal graph is precisely an inclusion-maximal
independent set of the \((r,r+1)\)-sparsity matroid on \(E(K_n)\). Hence it is a
basis. All such graphs therefore have the same number of edges.

## Step 4: compute the rank for every required order

Every sparse edge set on \(n\) vertices has at most

\[
rn-(r+1)
\tag{2}
\]

edges. It remains to show that equality is attainable for every \(n\ge2r\),
which is exactly the conjecture's range \(n\ge2k+2\).

Start at \(n=2r\) with \(K_{2r}\) minus one edge. It has

\[
\binom{2r}{2}-1=2r^2-r-1=r(2r)-(r+1)
\]

edges. To check sparsity, let a nonempty edge subset use \(s\) vertices. For
\(2\le s\le2r-1\),

\[
\binom{s}{2}\le rs-r-1.
\]

Indeed, the difference on the right is a concave quadratic in \(s\), so its
minimum over this interval is at an endpoint; at both \(s=2\) and
\(s=2r-1\) it equals \(r-2\ge0\). At \(s=2r\), the one deleted edge gives
exactly the bound in (2).

For each additional vertex \(v\), add exactly \(r\) edges from \(v\) to
distinct old vertices. This zero-extension preserves sparsity. For a nonempty
edge set \(F\) containing \(q\) new edges:

- if \(q=0\), then \(F=F_0\) and the old graph's sparsity applies;
- if \(q\ge1\) and its old part \(F_0\) is nonempty, then \(q\le r\), the new
  vertex belongs to \(V(F)\), and
  \[
  |F|\le r|V(F_0)|-(r+1)+r\le r|V(F)|-(r+1);
  \]
- if \(F_0\) is empty, then \(q\ge1\), \(F\) is a \(q\)-edge star, and
  \[
  q\le r(q+1)-(r+1)=rq-1
  \]
  because \(r\ge2\) and \(q\ge1\).

Each extension adds \(r\) edges, so equality in (2) persists. Therefore the
matroid rank is \(rn-(r+1)\), and every basis has

\[
rn-(r+1)=(k+1)(n-1)-1
\]

edges. This proves Conjecture 1.

## Exact finite cross-check

[`verify.py`](verify.py) contains
two intentionally separate exact checks:

1. a direct test for a packing subgraph using the Nash--Williams--Tutte
   partition criterion;
2. the induced-subset count for \((r,r+1)\)-sparsity.

The tests exhaustively compare them on all 1,024 labeled graphs at
\((r,n)=(2,5)\) and all 32,768 labeled graphs at \((r,n)=(3,6)\). They also
enumerate the smallest conjectural case \(k=2,n=6\) directly. Exactly 15
labeled \(\tau_2\)-maximal graphs occur: one for each deleted edge of \(K_6\),
and every one has 14 edges. The explicit tight construction is separately
checked for \(r=2,3,4\) and four consecutive orders beginning at \(2r\).

Run the checks with:

```bash
uv run pytest -q
```

These finite checks are regression evidence for the translation and edge-case
handling. The proof itself is the matroid argument above.

## Publication state

Completed before recording this result:

1. two independent agent passes derived the same sparsity reduction and rank
   argument;
2. the second pass added and audited the self-contained exchange-axiom proof;
3. direct Nash--Williams--Tutte enumeration checked the first nontrivial finite
   cases independently of the sparsity predicate;
4. authenticated X freshness searches and broader web searches used the exact
   title, arXiv identifier, author names, `tau_k-maximal`, tree-packing, and
   sparsity-matroid terms without finding a prior proof or disproof.

The note is not peer reviewed, and Wang and Tian have not been contacted. Those
facts should be disclosed on any immediate public post; they do not prevent
posting a transparent proof note with code. Author notification and expert
review remain valuable follow-ups, especially for locating prior art. The
result should be presented as a short proof of their conjecture, not as a
counterexample.
