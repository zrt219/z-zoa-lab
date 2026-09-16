"""Test provenance tracking and lineage generation."""

from research.provenance.tracker import ProvenanceTracker


def test_provenance_tracker():
    tracker = ProvenanceTracker()
    rec = tracker.add(
        action="coordinate_transform",
        source="CF4 Table 2",
        inputs={"ra": 10.5, "dec": -20.2},
        outputs={"l": 204.1, "b": -70.5},
        formula="Astropy SkyCoord(icrs).galactic",
        reference_frame="GALACTIC",
    )

    assert rec.action == "coordinate_transform"
    assert rec.record_id is not None
    assert len(tracker.get_records()) == 1

    records_json = tracker.to_list()
    assert len(records_json) == 1
    assert records_json[0]["formula"] == "Astropy SkyCoord(icrs).galactic"
