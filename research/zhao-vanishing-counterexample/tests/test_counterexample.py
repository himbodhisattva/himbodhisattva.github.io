import json
from pathlib import Path

import pytest

import verify_counterexample as vc


@pytest.fixture(scope="module")
def construction() -> dict[str, object]:
    return vc.construct_quartic(vc.degree_three_input())


def test_degree_three_input_has_constant_jacobian_and_collision() -> None:
    vc.verify_degree_three_input(vc.degree_three_input())


def test_serialized_quartic_has_exact_collision() -> None:
    artifact_path = Path(__file__).parents[1] / "artifacts" / "counterexample.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    vc.verify_serialized_artifact(artifact)
    assert artifact["metrics"] == {
        "cubic_homogeneous_dimension": 23,
        "cubic_homogeneous_terms": 65,
        "quartic_dimension": 46,
        "quartic_terms": 410,
    }


def test_committed_artifact_matches_the_construction(construction: dict[str, object]) -> None:
    artifact_path = Path(__file__).parents[1] / "artifacts" / "counterexample.json"
    committed = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert vc.artifact_from_construction(construction) == committed
    assert (
        vc.check_artifact(construction, artifact_path)
        == "b719b1a64d83b96c19455e4292c9f02778335374632bce8d7dcb9bd7b686dfd2"
    )


def test_artifact_check_rejects_drift(tmp_path: Path, construction: dict[str, object]) -> None:
    artifact_path = tmp_path / "counterexample.json"
    vc.emit_artifact(construction, artifact_path)
    artifact_path.write_bytes(artifact_path.read_bytes() + b" ")

    with pytest.raises(ValueError, match="differs from the exact regenerated artifact"):
        vc.check_artifact(construction, artifact_path)
