"""Unit tests for canonical serialization, hashing, and memo encoding."""

import json
from research.ledger.canonicalize import (
    canonical_serialize,
    compute_sha256,
    build_canonical_anchor_manifest,
    compute_anchor_payload_hash,
)
from xrpl.utils import str_to_hex, hex_to_str


def test_deterministic_canonical_serialization():
    # Different insertion orders must produce identical byte representations
    data1 = {"b": 2, "a": 1, "z": {"k2": "v2", "k1": "v1"}}
    data2 = {"z": {"k1": "v1", "k2": "v2"}, "a": 1, "b": 2}

    bytes1 = canonical_serialize(data1)
    bytes2 = canonical_serialize(data2)

    assert bytes1 == bytes2
    assert b" " not in bytes1  # No whitespace in separators


def test_identical_input_identical_sha256(tmp_path):
    # Setup test run directory
    run_dir = tmp_path / "RUN_TEST"
    run_dir.mkdir()

    manifest_content = {
        "run_id": "RUN_TEST",
        "git_commit": "abc1234",
        "manifest_sha256": "feedface0000",
        "datasets": [{"id": "ds1", "hash": "h1"}],
        "outputs": {"val": 42.0},
    }
    with open(run_dir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest_content, f)

    with open(run_dir / "config.yaml", "w", encoding="utf-8") as f:
        f.write("param: true\n")

    with open(run_dir / "results.json", "w", encoding="utf-8") as f:
        json.dump({"metric": 0.99}, f)

    payload1 = build_canonical_anchor_manifest(run_dir, stage="PREDICTION_FROZEN")
    payload2 = build_canonical_anchor_manifest(run_dir, stage="PREDICTION_FROZEN")

    hash1 = compute_anchor_payload_hash(payload1)
    hash2 = compute_anchor_payload_hash(payload2)

    assert hash1 == hash2
    assert len(hash1) == 64


def test_changed_manifest_byte_different_sha256(tmp_path):
    run_dir = tmp_path / "RUN_MUTATE"
    run_dir.mkdir()

    manifest_content = {
        "run_id": "RUN_MUTATE",
        "git_commit": "abc1234",
        "manifest_sha256": "feedface0000",
        "datasets": [{"id": "ds1"}],
        "outputs": {"val": 1.0},
    }
    with open(run_dir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest_content, f)

    payload_before = build_canonical_anchor_manifest(run_dir, stage="PREDICTION_FROZEN")
    hash_before = compute_anchor_payload_hash(payload_before)

    # Mutate 1 byte in results
    with open(run_dir / "results.json", "w", encoding="utf-8") as f:
        json.dump({"val": 1.0000001}, f)

    payload_after = build_canonical_anchor_manifest(run_dir, stage="PREDICTION_FROZEN")
    hash_after = compute_anchor_payload_hash(payload_after)

    assert hash_before != hash_after


def test_memo_encode_decode_round_trip():
    memo_dict = {
        "p": "Z-ZOA",
        "r": "VELA-0017",
        "s": "PREDICTION_FROZEN",
        "h": "97b6a941e7f9185a539a9fcf7ff4fa65b058c6792372d6ca0cb646f88219abf2",
        "prev": "4F8A73D097B6A941E7F9185A539A9FCF7FF4FA65B058C6792372D6CA0CB646F8",
    }
    compact_json = json.dumps(memo_dict, separators=(",", ":"))
    hex_data = str_to_hex(compact_json)

    # Check serialized size is tiny (< 1 KB)
    assert len(compact_json) < 250
    assert len(hex_data) < 500

    decoded_json = hex_to_str(hex_data)
    recovered = json.loads(decoded_json)

    assert recovered == memo_dict
