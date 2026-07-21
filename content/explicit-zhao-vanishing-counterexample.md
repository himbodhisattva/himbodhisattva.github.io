---
title: "an explicit counterexample to Zhao's Vanishing Conjecture"
description: "The new three-variable Jacobian counterexample yields an explicit 46-variable quartic counterexample to Zhao's Vanishing Conjecture."
---

# an explicit counterexample to Zhao's Vanishing Conjecture

on july 19, 2026, [levent alpöge posted an explicit counterexample](https://x.com/__alpoge__/status/2079028340955197566) to the jacobian conjecture in three variables. the map has constant nonzero jacobian determinant and sends three different points to the same place. the construction has also been [checked in lean](https://github.com/deancureton/jacobian/blob/main/Jacobian/Counterexample.lean).

so the jacobian conjecture is false in every dimension at least three. the two-variable case is still open.

i asked codex to go counterexample hunting. it did not magically break ryser, seymour's second-neighborhood conjecture, or frankl's union-closed sets conjecture. it did find a more grounded casualty of the jacobian counterexample: an explicit homogeneous quartic that refutes Zhao's Vanishing Conjecture.

## the result

there is an explicit homogeneous quartic

`P in Q(i)[A1,...,A23,B1,...,B23]`

with 410 terms such that:

- `Hess(P)` is nilpotent;
- the map `Z - grad(P)` sends three distinct exact points to the same image;
- `Delta^m(P^m) = 0` for every positive `m`; and
- `Delta^m(P^(m+1))` is nonzero for infinitely many `m`.

the last two lines say exactly that `P` is a counterexample to the homogeneous quartic Vanishing Conjecture in [Zhao's formulation](https://arxiv.org/abs/math/0409534v2).

this is not only an existence argument. the polynomial, all three collision points, and their common image are serialized over `Q(i)` in a machine-readable certificate. the verifier reconstructs the 410-term polynomial, differentiates it, and checks the collision with exact arithmetic.

## where it comes from

the extraction is a chain of old reductions applied to the new map:

1. start with a public 11-variable degree-at-most-three stable lift of alpöge's map, [posted by Spacerat](https://gist.github.com/Spacerat/08b4a43f6b6ca57178efabc220170ce8/2224dace71e8763a8621a7f557bbc545a53aa820) and credited there to chatgpt. its full symbolic jacobian determinant is `-2`.
2. normalize the linear part and apply the [Bass-Connell-Wright reduction](https://doi.org/10.1090/S0273-0979-1982-15032-7). this produces a cubic-homogeneous map `Id + H` in 23 variables with nilpotent `JH` and an exact three-point collision.
3. apply the [de Bondt-van den Essen symmetric lift](https://doi.org/10.1090/S0002-9939-05-07570-2). this produces the quartic `P` in 46 variables with nilpotent hessian and carries the collision to `Id - grad(P)`.
4. Zhao's inversion formula turns eventual vanishing of `Delta^m(P^(m+1))` into a polynomial inverse for `Id - grad(P)`. the collision makes that impossible.

the verifier checks the original determinant, the normalization and homogeneous decomposition, the block identities behind the 23-variable nilpotence argument, and every collision. the 46-variable hessian step and the laplacian consequences use the cited published theorems rather than an expanded symbolic matrix power.

## code and certificate

- [self-contained source and proof sketch](https://github.com/himbodhisattva/himbodhisattva.github.io/tree/8088b825bb001ac75ff7d547b5bf82e37f55f1a0/research/zhao-vanishing-counterexample)
- [exact 410-term certificate](https://raw.githubusercontent.com/himbodhisattva/himbodhisattva.github.io/8088b825bb001ac75ff7d547b5bf82e37f55f1a0/research/zhao-vanishing-counterexample/artifacts/counterexample.json)
- [verification script](https://github.com/himbodhisattva/himbodhisattva.github.io/blob/8088b825bb001ac75ff7d547b5bf82e37f55f1a0/research/zhao-vanishing-counterexample/verify_counterexample.py)

the certificate's sha-256 is `b719b1a64d83b96c19455e4292c9f02778335374632bce8d7dcb9bd7b686dfd2`. four exact tests pass.

## epistemic status

this is a conventional computer-assisted proof built from exact finite checks and published reduction theorems. multiple independent audit passes found no remaining algebraic or sign error; one of them caught an important sign before publication.

it has not been peer reviewed, and I am not claiming priority. [Z. Zhang's july 20 note](https://zzhang-iu.github.io/papers/direct-consequences-jacobian/) already records the failure of Zhao's conjecture as an existential consequence of the new jacobian counterexample and asks for a small explicit quartic. this is one concrete extraction: 46 variables, 410 terms, exact collision included.
