# An explicit quartic counterexample to Zhao's Vanishing Conjecture

This repository gives an exact specification of a homogeneous quartic

\[
P\in \mathbb{Q}(i)[A_1,\ldots,A_{23},B_1,\ldots,B_{23}]
\]

with the following properties:

1. `Hess(P)` is nilpotent.
2. The polynomial map `Id - grad(P)` has three distinct inputs with the same output.

Consequently, with

\[
\Delta=\sum_{j=1}^{46}\frac{\partial^2}{\partial Z_j^2},
\]

Zhao's criterion gives

\[
\Delta^m(P^m)=0\quad\text{for every }m\ge 1,
\]

while

\[
\Delta^m(P^{m+1})\ne 0
\]

for infinitely many `m`. Thus `P` is a counterexample to the homogeneous quartic
Vanishing Conjecture.

Status, July 20, 2026: the finite algebraic certificates are checked with exact symbolic
arithmetic, and the nilpotence and Laplacian implications use published reduction
theorems. This is a conventional computer-assisted proof whose two main nilpotence
bridges rest on published theorems. It has not been machine-formalized or peer reviewed.
A current web search found no earlier explicit quartic
extracted from the July 19 Jacobian counterexample, but that is not a claim of priority.

## Certificate at a glance

| Object | Size |
|---|---:|
| Public degree-at-most-three Jacobian map | 11 variables, 52 terms |
| Cubic-homogeneous lift `Id + H` | 23 variables, 65 terms in `H` |
| Quartic `P` | 46 variables, 410 terms |
| Noninjectivity certificate | 3 exact points in `Q(i)^46` |

The canonical sparse polynomial and collision certificate are in
[`artifacts/counterexample.json`](artifacts/counterexample.json). Coefficients are encoded as
`[[real numerator, real denominator], [imaginary numerator, imaginary denominator]]`.

## Construction

### 1. Start with the 11-variable degree-three map

The script begins with the factor-aware 11-variable lift posted by GitHub user
[`Spacerat`](https://gist.github.com/Spacerat/08b4a43f6b6ca57178efabc220170ce8/2224dace71e8763a8621a7f557bbc545a53aa820),
whose file credits ChatGPT for the explicit construction. The source revision used here is
`2224dace71e8763a8621a7f557bbc545a53aa820`. That map is a stable degree reduction of
[Levent Alpöge's July 19 counterexample](https://x.com/__alpoge__/status/2079028340955197566).

For independence from the lift's derivation, this repository directly checks its full
11-by-11 symbolic Jacobian determinant:

\[
\det J\Phi=-2.
\]

It also checks the three stated rational inputs and their common image. If `A=JΦ(0)`, then
`det(A)=-2`, so

\[
E=A^{-1}\Phi=X+E_2+E_3
\]

has identity linear part, constant Jacobian determinant one, and the same collision. Here
`E_2` and `E_3` are homogeneous of degrees two and three.

### 2. Make the nonlinear Jacobian nilpotent

Following Bass, Connell, and Wright, introduce 11 variables `Y` and set

\[
N(X,Y)=(E_2(X)+Y,-E_3(X)).
\]

Writing `JE_k` for the Jacobian of `E_k`, a block determinant gives

\[
\det(I+uJN)=\det(I+uJE_2+u^2JE_3)=\det JE(uX)=1.
\]

It follows that the characteristic polynomial of `JN` is `lambda^22`. By
Cayley-Hamilton, `JN^22=0` in the polynomial matrix ring.

Split `N=N_1+N_2+N_3` into homogeneous pieces and introduce one more variable `t`:

\[
H(X,Y,t)=t^2N_1(X,Y)+tN_2(X,Y)+N_3(X,Y),
\]

with final component zero. The map `Id + H` is cubic homogeneous in 23 variables. If
`q=(X,Y)`, the upper-left block of the full Jacobian is

\[
J_qH(q,t)=t^2JN(q/t),
\]

and the last row is zero. Therefore the characteristic polynomial of `JH` is
`lambda^23`, first for nonzero `t` and then identically as a polynomial. Thus `JH^23=0`
in the polynomial matrix ring. At `t=1`, the map retains the three-point collision. The
verifier checks both displayed matrix identities symbolically.

### 3. Apply the symmetric lift

For `U,V in C^23`, define

\[
f(U,V)=-i\sum_{j=1}^{23}H_j(U+iV)V_j,
\qquad P=-f.
\]

Lemma 1.2 of de Bondt and van den Essen says that `Hess(f)` is nilpotent if
and only if `JH` is nilpotent. Negating a matrix preserves nilpotence, so `Hess(P)` is
nilpotent. The sign `P=-f` is important because Zhao writes the associated map as
`Id - grad(P)`.

There is also a finite collision certificate. If `z` is one of the three colliding inputs for
`Id + H`, put

\[
r=(I+JH(z)^T)^{-1}H(z),
\qquad w=(z+r,ir).
\]

The inverse exists because `JH(z)` is nilpotent. Direct substitution shows that the three
resulting points `w` have the same image under `Id - grad(P)`. The JSON artifact contains
all coordinates, and the verifier recomputes the images from the expanded 410-term
quartic.

## Why this refutes the Vanishing Conjecture

For a homogeneous quartic `P`, Zhao's Vanishing Conjecture is the implication

\[
\left[\Delta^m(P^m)=0\text{ for every }m\ge1\right]
\Longrightarrow
\left[\Delta^m(P^{m+1})=0\text{ for all sufficiently large }m\right].
\]

Two results from Zhao's paper finish the argument:

- Theorem 4.3 says Hessian nilpotence of `P` is equivalent to
  `Delta^m(P^m)=0` for every `m >= 1`.
- Theorem 3.4 gives the deformed inversion-pair formula. If
  `F_t=Z-t grad(P)`, its formal inverse has the form `F_t^(-1)=Z+t grad(Q_t)`, where

  \[
  Q_t=\sum_{m\ge0}
  \frac{t^m}{2^m m!(m+1)!}\Delta^m(P^{m+1}).
  \]

If `Delta^m(P^(m+1))` vanished eventually, `Q_t` would be a polynomial. Specializing the
resulting polynomial inverse at `t=1` would give an inverse to `Id - grad(P)`. The exact
collision rules out any inverse. Therefore the sequence is nonzero for infinitely many
`m`.

## Reproduce

```bash
uv sync --frozen --dev
uv run --frozen python verify_counterexample.py --check artifacts/counterexample.json
uv run --frozen pytest
uv run --frozen ruff check .
```

The `--check` command regenerates the artifact in memory, compares it byte for byte with
the committed file, and verifies its adjacent SHA-256 file without overwriting either.
Use `--emit PATH` only to write a fresh copy to a separate path. The complete test suite
takes roughly 40 seconds on the development machine with Python 3.13.5 and uv 0.8.0.

The verifier computes the full 11-variable determinant `-2` over the exact polynomial
ring, checks every normalization and homogeneous decomposition identity, and carries the
collisions through the BCW and symmetric lifts. It also checks homogeneity and term counts,
round-trips the canonical JSON certificate, differentiates the serialized quartic, and
rechecks the final three-point collision.

The verifier checks the block identities that imply nilpotence of the 23-variable cubic
Jacobian. Nilpotence of the 46-variable Hessian then follows from the cited symmetric-lift
lemma rather than from expanding a 46-by-46 symbolic matrix power.

## Provenance and attribution

- The original three-variable Jacobian counterexample was announced by Levent Alpöge,
  crediting Akhil for the question and Fable for the construction.
- The 11-variable degree-three lift used here was posted by GitHub user `Spacerat`; its
  source credits ChatGPT. This repository does not claim that lift.
- This repository composes that lift with the published BCW and symmetric reductions,
  carries exact collisions through the construction, and serializes the resulting
  23-variable cubic-homogeneous and 46-variable quartic consequences.

## References

- H. Bass, E. H. Connell, and D. Wright, [The Jacobian Conjecture: Reduction of Degree and
  Formal Expansion of the Inverse](https://doi.org/10.1090/S0273-0979-1982-15032-7),
  *Bulletin of the AMS* 7 (1982), 287-330.
- M. de Bondt and A. van den Essen, [A Reduction of the Jacobian Conjecture to the
  Symmetric Case](https://doi.org/10.1090/S0002-9939-05-07570-2), *Proceedings of the AMS*
  133 (2005), 2201-2205.
- W. Zhao, [Hessian Nilpotent Polynomials and the Jacobian
  Conjecture](https://arxiv.org/abs/math/0409534v2), arXiv v2, 2004.
- Z. Zhang, [Direct Consequences of the Three-Dimensional Counterexample to the Jacobian
  Conjecture](https://zzhang-iu.github.io/papers/direct-consequences-jacobian/), July 20,
  2026. This note records the Vanishing Conjecture consequence existentially and asks for
  a small explicit quartic.
