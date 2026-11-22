"""Verify archived numerical results, source fingerprints, and figure files."""

import argparse
from hashlib import sha256
import json
import math
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def main(output):
    initial = pd.read_csv(DATA / "initial_validation_cases.csv")
    two = initial[initial.group.str.startswith("two_")]
    assert len(two) == 240
    expected = {
        "fixed3": (139, [240, 0, 0]),
        "boundary": (206, [117, 85, 38]),
        "difference": (238, [98, 115, 27]),
        "proposed": (238, [126, 108, 6]),
    }
    for method, (passed, qubits) in expected.items():
        assert int(two[method + "_pass"].sum()) == passed
        observed = [
            int((two[method + "_photon_qubits"] == count).sum())
            for count in (2, 3, 4)
        ]
        assert observed == qubits
    assert int(initial[initial.group == "one_holdout"].proposed_pass.sum()) == 64

    follow = pd.read_csv(DATA / "followup_cases.csv")
    new = follow[follow.group.isin(["broad", "polariton", "strong_drive"])]
    assert len(new) == 192
    assert int(new.guard_cutoff_pass.sum()) == 192
    assert int(new.pilot_cutoff_pass.sum()) == 191
    assert int((new.guard_qubits > new.pilot_qubits).sum()) == 14

    antibunched = new[new.reference_g2 < 1]
    feasible = antibunched[
        antibunched.precision_shot_plan_pass & antibunched.decision_shot_plan_pass
    ]
    assert len(antibunched) == 50 and len(feasible) == 36
    assert int(new.precision_shot_plan_pass.sum()) == 138
    assert int(antibunched.decision_shot_plan_pass.sum()) == 42
    ratio = float((feasible.precision_shots_used / feasible.decision_shots_used).median())
    assert abs(ratio - 12.589258666639873) < 1e-9

    strong = antibunched[antibunched.reference_g2 < 0.9]
    assert len(strong) == 41
    assert int((strong.decision_batch_antibunching >= 0.95 * 256).sum()) == 39
    assert int(new[new.reference_g2 >= 1].decision_batch_antibunching.sum()) == 0
    assert int(follow[follow.group == "empty"].decision_batch_antibunching.sum()) == 2

    pilot = pd.read_csv(DATA / "finite_pilot_counts.csv")
    trials = pd.read_csv(DATA / "finite_pilot_trials.csv")
    assert len(pilot) == 4608 and len(trials) == 36864
    allocated = (
        trials.shots_00.fillna(0)
        + trials.shots_11.fillna(0)
        + trials.science_shots.fillna(0)
    )
    assert ((trials.total_spent - trials.pilot_total) == allocated).all()

    hardware = pd.read_csv(DATA / "hardware_readout_results.csv")
    assert len(hardware) == 4 and hardware.target_covered.sum() == 4
    widths = {
        (row.arm, row.population): row.interval_upper - row.interval_lower
        for _, row in hardware.iterrows()
    }
    signal_reduction = (
        1 - widths["selected_allocation", "signal"] / widths["reference_allocation", "signal"]
    )
    control_increase = (
        widths["selected_allocation", "control"] / widths["reference_allocation", "control"] - 1
    )
    assert abs(signal_reduction - 0.2702) < 0.0001
    assert abs(control_increase - 0.2709) < 0.0001

    targets = json.loads((DATA / "hardware_targets.json").read_text())
    for population in ("signal", "control"):
        probabilities = targets[population]["probabilities"]
        mean = sum(number * value for number, value in enumerate(probabilities))
        correlation = (
            sum(number * (number - 1) * value for number, value in enumerate(probabilities))
            / mean**2
        )
        assert math.isclose(correlation, targets[population]["target_g2"], rel_tol=1e-13)

    acquisition = json.loads((DATA / "hardware_analysis_manifest.json").read_text())
    assert acquisition["actual_device_shots"] == 608256
    assert acquisition["actual_hardware_jobs"] == 32

    audit = json.loads((DATA / "verification_analysis.json").read_text())
    assert audit["status"] == "verified"
    assert audit["reference_cases"] == 217
    assert audit["record_hashes_verified"] == 225

    power = json.loads((DATA / "replication_validation_summary.json").read_text())
    assert power["matched_model_goals_met"]
    assert power["planned_hardware_pairs"] == 64
    assert not power["within_resource_target"]
    assert math.isclose(
        power["minimum_validation_study_power_lower_bound"], 0.9234054381487532
    )

    for extension in ("png", "pdf", "svg"):
        assert len(list((ROOT / "figures").glob("*." + extension))) == 12
    for record in json.loads((DATA / "source_fingerprints.json").read_text()):
        assert sha256((ROOT / record["file"]).read_bytes()).hexdigest() == record["sha256"]
    for record in json.loads((ROOT / "evidence/source_archives.json").read_text()):
        assert sha256((ROOT / record["file"]).read_bytes()).hexdigest() == record["sha256"]

    record = {
        "status": "passed",
        "initial_two_emitter_cases": len(two),
        "initial_moment_weighted_passes": int(two.proposed_pass.sum()),
        "new_guard_cases": len(new),
        "new_guard_passes": int(new.guard_cutoff_pass.sum()),
        "numerical_audit_records": audit["record_hashes_verified"],
        "finite_pilots": len(pilot),
        "paired_planning_rows": len(trials),
        "figure_count": 12,
        "actual_device_shots": acquisition["actual_device_shots"],
        "actual_hardware_jobs": acquisition["actual_hardware_jobs"],
        "signal_interval_width_reduction": signal_reduction,
        "control_interval_width_increase": control_increase,
        "median_precision_to_decision_shot_ratio": ratio,
        "prospective_comparison_pairs": power["planned_hardware_pairs"],
        "prospective_power_lower_bound": power["minimum_validation_study_power_lower_bound"],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "reproduced" / "validation_record.json",
        help="save the numerical verification record at this path",
    )
    main(parser.parse_args().output)
