from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp
from sympy.polys.matrices import DomainMatrix


def _monomial(variables: list[sp.Symbol], powers: tuple[int, ...]) -> sp.Expr:
    result = sp.Integer(1)
    for variable, exponent in zip(variables, powers, strict=True):
        result *= variable**exponent
    return result


def _homogeneous_part(expression: sp.Expr, variables: list[sp.Symbol], degree: int) -> sp.Expr:
    polynomial = sp.Poly(expression, *variables)
    return sp.Add(
        *(
            coefficient * _monomial(variables, powers)
            for powers, coefficient in polynomial.terms()
            if sum(powers) == degree
        )
    )


def degree_three_input() -> dict[str, Any]:
    """Return the public 11-variable degree-three lift and its collision."""
    x, y, z, a, b, c, d, q, s, h, k = sp.symbols("x y z a b c d q s h k")
    variables = [x, y, z, a, b, c, d, q, s, h, k]
    mapping = [
        -a * c
        - a * d * z
        - 3 * a * y**2
        - 2 * a * z
        - c * d**2
        + d**2 * z
        - d * s
        + 7 * d * y**2
        + s * x * y
        + 3 * x * y * z
        + 4 * y**2
        + z,
        -b * c
        - b * d * z
        - 3 * b * y**2
        - 2 * b * z
        - 3 * c * d * x
        - d * q
        + q * x * y
        + 12 * x * y**2
        + 3 * x * z
        + y,
        -h * k - h * x * z + k * x**2 - 3 * x**2 * y + 2 * x,
        a - d**2 + 2 * d * x * y,
        b + 3 * x**2 * y,
        c + x * y * z + 3 * y**2 + 2 * z,
        d - x * y,
        b * z + 3 * c * x + q,
        s + a * z + c * x * y - x * y * z - 7 * y**2 + c * d - d * z,
        h - x**2,
        k + x * z,
    ]
    collision_points = [
        [0, 0, -sp.Rational(1, 4), 0, 0, sp.Rational(1, 2), 0, 0, 0, 0, 0],
        [
            1,
            -sp.Rational(3, 2),
            sp.Rational(13, 2),
            -sp.Rational(9, 4),
            sp.Rational(9, 2),
            -10,
            -sp.Rational(3, 2),
            sp.Rational(3, 4),
            -sp.Rational(153, 8),
            1,
            -sp.Rational(13, 2),
        ],
        [
            -1,
            sp.Rational(3, 2),
            sp.Rational(13, 2),
            -sp.Rational(9, 4),
            -sp.Rational(9, 2),
            -10,
            -sp.Rational(3, 2),
            -sp.Rational(3, 4),
            -sp.Rational(153, 8),
            1,
            sp.Rational(13, 2),
        ],
    ]
    return {
        "variables": variables,
        "mapping": [sp.expand(expression) for expression in mapping],
        "collision_points": collision_points,
        "common_image": [-sp.Rational(1, 4)] + [sp.Integer(0)] * 10,
    }


def verify_degree_three_input(data: dict[str, Any]) -> None:
    variables = data["variables"]
    mapping = data["mapping"]
    collision_points = data["collision_points"]
    common_image = data["common_image"]

    assert max(sp.Poly(expression, *variables).total_degree() for expression in mapping) == 3
    assert sum(len(sp.Poly(expression, *variables).terms()) for expression in mapping) == 52
    assert len({tuple(point) for point in collision_points}) == 3
    for point in collision_points:
        substitutions = dict(zip(variables, point, strict=True))
        assert [expression.subs(substitutions) for expression in mapping] == common_image

    jacobian = sp.Matrix(mapping).jacobian(variables)
    assert DomainMatrix.from_Matrix(jacobian).det().as_expr() == -2


def construct_quartic(input_data: dict[str, Any]) -> dict[str, Any]:
    """Apply BCW homogenization and the de Bondt--van den Essen symmetric lift."""
    variables = input_data["variables"]
    mapping = input_data["mapping"]
    collision_points = input_data["collision_points"]
    common_image = input_data["common_image"]

    linear_part = (
        sp.Matrix(mapping).jacobian(variables).subs({variable: 0 for variable in variables})
    )
    assert linear_part.det() == -2
    normalized = [sp.expand(expression) for expression in linear_part.inv() * sp.Matrix(mapping)]
    assert sp.Matrix(normalized).jacobian(variables).subs(
        {variable: 0 for variable in variables}
    ) == sp.eye(len(variables))
    normalized_image = list(linear_part.inv() * sp.Matrix(common_image))
    for point in collision_points:
        substitutions = dict(zip(variables, point, strict=True))
        assert [expression.subs(substitutions) for expression in normalized] == normalized_image

    quadratic = [
        _homogeneous_part(expression - variable, variables, 2)
        for expression, variable in zip(normalized, variables, strict=True)
    ]
    cubic = [
        _homogeneous_part(expression - variable, variables, 3)
        for expression, variable in zip(normalized, variables, strict=True)
    ]
    assert all(
        sp.expand(expression - variable - degree_two - degree_three) == 0
        for expression, variable, degree_two, degree_three in zip(
            normalized, variables, quadratic, cubic, strict=True
        )
    )

    # The BCW nilpotence certificate reduces to an 11-by-11 matrix identity.
    # For N=(E_2+Y,-E_3), a block determinant gives
    # det(I+u*JN)=det(I+u*JE_2+u^2*JE_3)=det(JE(uX))=1.
    rank = len(variables)
    parameter = sp.Symbol("parameter")
    normalized_jacobian = sp.Matrix(normalized).jacobian(variables)
    assert normalized_jacobian == linear_part.inv() * sp.Matrix(mapping).jacobian(variables)
    scaled_substitutions = {variable: parameter * variable for variable in variables}
    scaled_normalized_jacobian = normalized_jacobian.subs(scaled_substitutions, simultaneous=True)
    reduced_block_determinant = (
        sp.eye(rank)
        + parameter * sp.Matrix(quadratic).jacobian(variables)
        + parameter**2 * sp.Matrix(cubic).jacobian(variables)
    )
    assert all(
        sp.expand(entry) == 0 for entry in scaled_normalized_jacobian - reduced_block_determinant
    )

    auxiliary = list(sp.symbols(f"u1:{rank + 1}"))
    unipotent_variables = variables + auxiliary
    unipotent_change = [
        degree_two + auxiliary_variable
        for degree_two, auxiliary_variable in zip(quadratic, auxiliary, strict=True)
    ] + [-degree_three for degree_three in cubic]
    unipotent_map = [
        variable + change
        for variable, change in zip(unipotent_variables, unipotent_change, strict=True)
    ]

    unipotent_points = []
    for point in collision_points:
        substitutions = dict(zip(variables, point, strict=True))
        cubic_value = [expression.subs(substitutions) for expression in cubic]
        unipotent_points.append(point + cubic_value)
    unipotent_images = [
        [
            expression.subs(dict(zip(unipotent_variables, point, strict=True)))
            for expression in unipotent_map
        ]
        for point in unipotent_points
    ]
    assert all(image == unipotent_images[0] for image in unipotent_images[1:])

    t = sp.Symbol("t")
    cubic_variables = unipotent_variables + [t]
    linear_change = [
        _homogeneous_part(change, unipotent_variables, 1) for change in unipotent_change
    ]
    quadratic_change = [
        _homogeneous_part(change, unipotent_variables, 2) for change in unipotent_change
    ]
    cubic_change_before_homogenizing = [
        _homogeneous_part(change, unipotent_variables, 3) for change in unipotent_change
    ]
    cubic_change = [
        sp.expand(linear * t**2 + degree_two * t + degree_three)
        for linear, degree_two, degree_three in zip(
            linear_change,
            quadratic_change,
            cubic_change_before_homogenizing,
            strict=True,
        )
    ] + [sp.Integer(0)]
    cubic_map = [
        variable + change for variable, change in zip(cubic_variables, cubic_change, strict=True)
    ]
    cubic_points = [point + [sp.Integer(1)] for point in unipotent_points]
    cubic_images = [
        [
            expression.subs(dict(zip(cubic_variables, point, strict=True)))
            for expression in cubic_map
        ]
        for point in cubic_points
    ]
    assert len({tuple(point) for point in cubic_points}) == 3
    assert all(image == cubic_images[0] for image in cubic_images[1:])
    assert all(
        change == 0
        or (
            sp.Poly(change, *cubic_variables).is_homogeneous
            and sp.Poly(change, *cubic_variables).total_degree() == 3
        )
        for change in cubic_change
    )

    # The top-left block of JH is t^2*JN(q/t). Since the last component of H
    # is zero, this is the finite polynomial identity used by homogenization.
    unipotent_jacobian = sp.Matrix(unipotent_change).jacobian(unipotent_variables)
    cubic_jacobian = sp.Matrix(cubic_change).jacobian(cubic_variables)
    homogenizing_substitutions = {variable: variable / t for variable in unipotent_variables}
    homogenized_jacobian = sp.expand(t**2 * unipotent_jacobian.subs(homogenizing_substitutions))
    assert cubic_jacobian[:-1, :-1] == homogenized_jacobian
    assert cubic_jacobian[-1, :] == sp.zeros(1, len(cubic_variables))

    dimension = len(cubic_variables)
    avariables = list(sp.symbols(f"A1:{dimension + 1}"))
    bvariables = list(sp.symbols(f"B1:{dimension + 1}"))
    substitution = {
        variable: avariable + sp.I * bvariable
        for variable, avariable, bvariable in zip(
            cubic_variables, avariables, bvariables, strict=True
        )
    }
    symmetric_lift = sp.expand(
        -sp.I
        * sum(
            change.subs(substitution) * bvariable
            for change, bvariable in zip(cubic_change, bvariables, strict=True)
        )
    )
    # Zhao writes the associated map as Id-grad(P). The symmetric lift gives
    # Id+grad(symmetric_lift), hence P is the negative of that lift.
    vanishing_polynomial = sp.expand(-symmetric_lift)
    quartic_variables = avariables + bvariables
    quartic_as_poly = sp.Poly(vanishing_polynomial, *quartic_variables)
    assert quartic_as_poly.total_degree() == 4
    assert quartic_as_poly.is_homogeneous

    zhao_points = []
    for point in cubic_points:
        substitutions_at_point = dict(zip(cubic_variables, point, strict=True))
        h_value = sp.Matrix([change.subs(substitutions_at_point) for change in cubic_change])
        matrix = sp.eye(dimension) + cubic_jacobian.subs(substitutions_at_point).T
        real_vector = matrix.inv() * h_value
        zhao_points.append(
            [value + offset for value, offset in zip(point, real_vector, strict=True)]
            + [sp.I * offset for offset in real_vector]
        )

    zhao_map = [
        variable - sp.diff(vanishing_polynomial, variable) for variable in quartic_variables
    ]
    zhao_images = [
        [
            sp.expand(expression.subs(dict(zip(quartic_variables, point, strict=True))))
            for expression in zhao_map
        ]
        for point in zhao_points
    ]
    assert len({tuple(point) for point in zhao_points}) == 3
    assert all(image == zhao_images[0] for image in zhao_images[1:])

    return {
        "cubic_variables": cubic_variables,
        "cubic_change": cubic_change,
        "cubic_points": cubic_points,
        "quartic_variables": quartic_variables,
        "vanishing_polynomial": vanishing_polynomial,
        "zhao_points": zhao_points,
        "zhao_common_image": zhao_images[0],
    }


def _gaussian_rational(value: sp.Expr) -> list[list[int]]:
    value = sp.expand(value)
    real, imaginary = value.as_real_imag()
    real = sp.Rational(real)
    imaginary = sp.Rational(imaginary)
    return [
        [int(real.p), int(real.q)],
        [int(imaginary.p), int(imaginary.q)],
    ]


def artifact_from_construction(construction: dict[str, Any]) -> dict[str, Any]:
    variables = construction["quartic_variables"]
    polynomial = sp.Poly(construction["vanishing_polynomial"], *variables)
    return {
        "schema_version": 1,
        "field": "Q(i)",
        "statement": "P is quartic Hessian-nilpotent, but Id-grad(P) is noninjective.",
        "variables": [str(variable) for variable in variables],
        "polynomial_terms": [
            {
                "exponents": list(powers),
                "coefficient": _gaussian_rational(coefficient),
            }
            for powers, coefficient in polynomial.terms()
        ],
        "collision_points": [
            [_gaussian_rational(value) for value in point] for point in construction["zhao_points"]
        ],
        "common_image": [_gaussian_rational(value) for value in construction["zhao_common_image"]],
        "metrics": {
            "cubic_homogeneous_dimension": len(construction["cubic_variables"]),
            "cubic_homogeneous_terms": sum(
                len(sp.Poly(change, *construction["cubic_variables"]).terms())
                for change in construction["cubic_change"]
            ),
            "quartic_dimension": len(variables),
            "quartic_terms": len(polynomial.terms()),
        },
    }


def _from_gaussian_rational(value: list[list[int]]) -> sp.Expr:
    (real_numerator, real_denominator), (imaginary_numerator, imaginary_denominator) = value
    return sp.Rational(real_numerator, real_denominator) + sp.I * sp.Rational(
        imaginary_numerator, imaginary_denominator
    )


def verify_serialized_artifact(artifact: dict[str, Any]) -> None:
    assert artifact["schema_version"] == 1
    assert artifact["field"] == "Q(i)"
    assert len(artifact["variables"]) == len(set(artifact["variables"])) == 46
    assert all(
        len(term["exponents"]) == len(artifact["variables"])
        and all(isinstance(exponent, int) and exponent >= 0 for exponent in term["exponents"])
        and all(
            isinstance(component, list)
            and len(component) == 2
            and all(isinstance(value, int) for value in component)
            and component[1] > 0
            for component in term["coefficient"]
        )
        for term in artifact["polynomial_terms"]
    )
    variables = list(sp.symbols(" ".join(artifact["variables"])))
    polynomial = sp.Add(
        *(
            _from_gaussian_rational(term["coefficient"])
            * _monomial(variables, tuple(term["exponents"]))
            for term in artifact["polynomial_terms"]
        )
    )
    polynomial_as_poly = sp.Poly(polynomial, *variables)
    assert polynomial_as_poly.is_homogeneous
    assert polynomial_as_poly.total_degree() == 4
    assert len(polynomial_as_poly.terms()) == artifact["metrics"]["quartic_terms"] == 410

    points = [
        [_from_gaussian_rational(value) for value in point]
        for point in artifact["collision_points"]
    ]
    expected_image = [_from_gaussian_rational(value) for value in artifact["common_image"]]
    assert len(points) == 3
    assert all(len(point) == len(variables) for point in points)
    assert len(expected_image) == len(variables)
    mapping = [variable - sp.diff(polynomial, variable) for variable in variables]
    assert len({tuple(point) for point in points}) == 3
    for point in points:
        substitutions = dict(zip(variables, point, strict=True))
        assert [
            sp.expand(expression.subs(substitutions)) for expression in mapping
        ] == expected_image


def _serialized_artifact(construction: dict[str, Any]) -> str:
    return (
        json.dumps(
            artifact_from_construction(construction), ensure_ascii=True, indent=2, sort_keys=True
        )
        + "\n"
    )


def emit_artifact(construction: dict[str, Any], output_path: Path) -> str:
    serialized = _serialized_artifact(construction)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(serialized, encoding="utf-8")
    digest = hashlib.sha256(serialized.encode()).hexdigest()
    output_path.with_suffix(output_path.suffix + ".sha256").write_text(
        f"{digest}  {output_path.name}\n", encoding="utf-8"
    )
    return digest


def check_artifact(construction: dict[str, Any], artifact_path: Path) -> str:
    expected = _serialized_artifact(construction).encode()
    actual = artifact_path.read_bytes()
    if actual != expected:
        raise ValueError(f"{artifact_path} differs from the exact regenerated artifact")

    digest = hashlib.sha256(actual).hexdigest()
    checksum_path = artifact_path.with_suffix(artifact_path.suffix + ".sha256")
    expected_checksum = f"{digest}  {artifact_path.name}\n"
    if checksum_path.read_text(encoding="utf-8") != expected_checksum:
        raise ValueError(f"{checksum_path} does not match {artifact_path}")
    return digest


def main() -> None:
    parser = argparse.ArgumentParser()
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--emit", type=Path, help="Write a regenerated JSON certificate")
    output_group.add_argument(
        "--check", type=Path, help="Compare an existing certificate with exact regeneration"
    )
    args = parser.parse_args()
    if not __debug__:
        parser.error("verification requires assertions; unset PYTHONOPTIMIZE and omit Python -O")

    input_data = degree_three_input()
    verify_degree_three_input(input_data)
    construction = construct_quartic(input_data)
    artifact = artifact_from_construction(construction)
    verify_serialized_artifact(artifact)

    print("Verified the exact construction and finite collision certificates")
    for key, value in artifact["metrics"].items():
        print(f"  {key}: {value}")
    nonzero_image = [
        (index + 1, _from_gaussian_rational(value))
        for index, value in enumerate(artifact["common_image"])
        if _from_gaussian_rational(value) != 0
    ]
    print(f"  common_image_nonzero_coordinates: {nonzero_image}")
    if args.emit:
        digest = emit_artifact(construction, args.emit)
        print(f"  artifact_sha256: {digest}")
    if args.check:
        digest = check_artifact(construction, args.check)
        print(f"  checked_artifact_sha256: {digest}")


if __name__ == "__main__":
    main()
