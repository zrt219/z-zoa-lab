"""Unit tests for survey footprints, selection functions, and ZoA masks (Prompt 08)."""

import numpy as np
import pytest

from research.masks.selection_functions import (
    SURVEY_FOOTPRINTS,
    SurveyFootprint,
    get_survey_footprint,
    is_inside_footprint,
    relative_detection_weight,
    valid_velocity_range,
    zoa_obscuration_mask,
)


class TestSurveyFootprints:
    def test_hizoa_footprint_and_wrap(self):
        """HIZOA footprint: |b| <= 5 deg, 210 deg <= l <= 360 deg and 0 deg <= l <= 30 deg, cz <= 12,000 km/s."""
        # Inside standard region
        assert is_inside_footprint("HIZOA", 250.0, 0.0) is True
        assert is_inside_footprint("HIZOA", 210.0, 5.0) is True
        assert is_inside_footprint("HIZOA", 359.0, -3.0) is True
        # Inside wraparound region (0 to 30 deg)
        assert is_inside_footprint("HIZOA", 15.0, 2.0) is True
        assert is_inside_footprint("HIZOA", 30.0, -5.0) is True

        # Outside longitude bounds
        assert is_inside_footprint("HIZOA", 100.0, 0.0) is False
        assert is_inside_footprint("HIZOA", 180.0, 0.0) is False
        assert is_inside_footprint("HIZOA", 45.0, 0.0) is False

        # Outside latitude bounds
        assert is_inside_footprint("HIZOA", 250.0, 7.0) is False
        assert is_inside_footprint("HIZOA", 250.0, -6.0) is False

        # Velocity range
        assert valid_velocity_range("HIZOA", 0.0) is True
        assert valid_velocity_range("HIZOA", 6000.0) is True
        assert valid_velocity_range("HIZOA", 12000.0) is True
        assert valid_velocity_range("HIZOA", 12500.0) is False
        assert valid_velocity_range("HIZOA", -10.0) is False

    def test_vela_smgps_footprint(self):
        """Vela-SMGPS: 260 deg <= l <= 290 deg, -2 deg <= b <= +1 deg, cz <= 25,000 km/s."""
        assert is_inside_footprint("VELA_SMGPS", 270.0, -1.0) is True
        assert is_inside_footprint("VELA_SMGPS", 260.0, 1.0) is True
        assert is_inside_footprint("VELA_SMGPS", 290.0, -2.0) is True

        # Outside
        assert is_inside_footprint("VELA_SMGPS", 255.0, 0.0) is False
        assert is_inside_footprint("VELA_SMGPS", 295.0, 0.0) is False
        assert is_inside_footprint("VELA_SMGPS", 275.0, 2.0) is False
        assert is_inside_footprint("VELA_SMGPS", 275.0, -3.0) is False

        # Velocity
        assert valid_velocity_range("VELA_SMGPS", 5000.0) is True
        assert valid_velocity_range("VELA_SMGPS", 25000.0) is True
        assert valid_velocity_range("VELA_SMGPS", 26000.0) is False

    def test_vela_hi_footprint(self):
        """Vela-HI: 263 deg <= l <= 284 deg, extended latitude, cz <= 25,000 km/s."""
        assert is_inside_footprint("VELA_HI", 270.0, -2.5) is True
        assert is_inside_footprint("VELA_HI", 263.0, 1.5) is True
        assert is_inside_footprint("VELA_HI", 284.0, -1.0) is True

        # Outside
        assert is_inside_footprint("VELA_HI", 260.0, 0.0) is False
        assert is_inside_footprint("VELA_HI", 286.0, 0.0) is False

        # Velocity
        assert valid_velocity_range("VELA_HI", 18000.0) is True
        assert valid_velocity_range("VELA_HI", 25000.0) is True
        assert valid_velocity_range("VELA_HI", 25100.0) is False

    def test_2mrs_mask(self):
        """2MRS: Near-infrared all-sky mask, |b| > 5 deg (optical/NIR ZoA extinction cutoff), cz <= 15,000 km/s."""
        assert is_inside_footprint("2MRS", 100.0, 25.0) is True
        assert is_inside_footprint("2MRS", 200.0, -30.0) is True

        # Masked in ZoA cutoff (|b| <= 5 deg)
        assert is_inside_footprint("2MRS", 100.0, 3.0) is False
        assert is_inside_footprint("2MRS", 250.0, -2.0) is False
        assert is_inside_footprint("2MRS", 0.0, 0.0) is False

        # Velocity completeness
        assert valid_velocity_range("2MRS", 8000.0) is True
        assert valid_velocity_range("2MRS", 15000.0) is True
        assert valid_velocity_range("2MRS", 16000.0) is False

    def test_cf4_mask(self):
        """CF4: Footprint and velocity completeness."""
        assert is_inside_footprint("CF4", 120.0, 45.0) is True
        assert is_inside_footprint("CF4", 120.0, 2.0) is False  # ZoA avoidance
        assert valid_velocity_range("CF4", 12000.0) is True
        assert valid_velocity_range("CF4", 30000.0) is True
        assert valid_velocity_range("CF4", 35000.0) is False


class TestRelativeDetectionWeight:
    def test_detection_weights_in_range(self):
        w1 = relative_detection_weight("HIZOA", cz_kms=3000.0, b_deg=0.0)
        assert 0.0 < w1 <= 1.0

        w_edge = relative_detection_weight("HIZOA", cz_kms=12000.0, b_deg=0.0)
        assert 0.0 <= w_edge <= w1

        # Out of velocity range -> 0.0
        assert relative_detection_weight("HIZOA", cz_kms=15000.0, b_deg=0.0) == 0.0

    def test_2mrs_extinction_weight(self):
        # Inside ZoA -> 0.0
        assert relative_detection_weight("2MRS", cz_kms=5000.0, b_deg=2.0) == 0.0
        # High latitude -> non-zero
        w_high = relative_detection_weight("2MRS", cz_kms=5000.0, b_deg=40.0)
        assert w_high > 0.0


class TestZoaObscurationMask:
    def test_galactic_frame_mask(self):
        mask = zoa_obscuration_mask(grid_shape=16, box_size_mpc=200.0, b_cut_deg=5.0, frame="galactic")
        assert mask.shape == (16, 16, 16)
        assert mask.dtype == bool

        # Obscured volume fraction should be in realistic geometric range (5% - 20%)
        frac = np.mean(mask)
        assert 0.03 < frac < 0.25

    def test_supergalactic_frame_mask(self):
        mask = zoa_obscuration_mask(grid_shape=(16, 16, 16), box_size_mpc=400.0, b_cut_deg=5.0, frame="supergalactic")
        assert mask.shape == (16, 16, 16)
        assert mask.dtype == bool
        frac = np.mean(mask)
        assert 0.03 < frac < 0.25

    def test_invalid_frame_raises(self):
        with pytest.raises(ValueError, match="Unsupported frame"):
            zoa_obscuration_mask(grid_shape=8, box_size_mpc=100.0, frame="invalid_frame")
