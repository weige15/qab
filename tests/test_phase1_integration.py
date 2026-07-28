import subprocess
import sys
from pathlib import Path


def test_no_gpu_manifest_resolution_prints_exact_assignments():
    repository_root = Path(__file__).parents[1]
    config = repository_root / "configs" / "issue-5-phase1.json"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "qcb.cli",
            "resolve-manifest",
            "--config",
            str(config),
        ],
        cwd=repository_root,
        check=True,
        capture_output=True,
        text=True,
    )

    lines = result.stdout.splitlines()
    assignment_lines = [line for line in lines if line.startswith("qcb.v1/") and "\tmodel.layers." in line]

    assert "resolved_without_execution" in result.stdout
    assert "\"capability_claim\": false" in result.stdout
    assert "qcb.v1/g4-equal7/B844\tmodel.layers.0.self_attn.q_proj\tlayer=0\tgroup=g00\trequested=BF16" in result.stdout
    assert "qcb.v1/g4-equal7/B844\tmodel.layers.27.mlp.down_proj\tlayer=27\tgroup=g03\trequested=W4A16" in result.stdout
    assert len(assignment_lines) == 14 * 28 * 7
    assert "weights loaded" not in result.stdout.lower()



def test_planned_preflight_records_the_full_run_contract(tmp_path):
    repository_root = Path(__file__).parents[1]
    config = repository_root / "configs" / "issue-5-phase1.json"
    run_root = tmp_path / "runs"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "qcb.cli",
            "preflight",
            "--config",
            str(config),
            "--run-root",
            str(run_root),
            "--run-id",
            "planned",
        ],
        cwd=repository_root,
        check=True,
        capture_output=True,
        text=True,
    )

    run_directory = run_root / "planned"
    required = {
        "resolved_config.yaml",
        "command.txt",
        "git_commit.txt",
        "environment.json",
        "hardware.json",
        "random_seeds.json",
        "metrics.json",
        "predictions.jsonl",
        "stdout.log",
        "stderr.log",
        "report.md",
    }
    assert {path.name for path in run_directory.iterdir()} == required
    assert '"capability_claim": false' in result.stdout
    assert '"status": "planned"' in (run_directory / "metrics.json").read_text()
