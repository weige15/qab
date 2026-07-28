import json

import pytest

from qcb.run_contract import REQUIRED_ARTIFACTS, RunContractError, create_run_directory


def _write_complete_contract(run):
    for name in REQUIRED_ARTIFACTS:
        if name.endswith(".json"):
            content = json.dumps({"status": "planned"})
        elif name == "predictions.jsonl":
            content = json.dumps({"status": "planned"}) + "\n"
        else:
            content = "planned\n"
        run.write_artifact(name, content)


def test_run_directory_is_unique_and_complete_artifacts_validate(tmp_path):
    run = create_run_directory(tmp_path, run_id="run-a")
    _write_complete_contract(run)

    validation = run.validate_artifacts()

    assert validation.valid
    assert validation.missing == ()
    assert validation.invalid == ()
    with pytest.raises(FileExistsError):
        create_run_directory(tmp_path, run_id="run-a")


def test_artifact_writes_are_write_once_and_missing_files_are_reported(tmp_path):
    run = create_run_directory(tmp_path, run_id="run-b")
    run.write_artifact("metrics.json", "{}\n")

    with pytest.raises(RunContractError, match="immutable"):
        run.write_artifact("metrics.json", "{}\n")

    validation = run.validate_artifacts()

    assert not validation.valid
    assert "report.md" in validation.missing
    assert "metrics.json" not in validation.missing
