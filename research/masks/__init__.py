"""Survey footprints and selection functions package for Z-ZOA."""

from research.masks.selection_functions import (
    SurveyFootprint,
    SURVEY_FOOTPRINTS,
    get_survey_footprint,
    is_inside_footprint,
    valid_velocity_range,
    relative_detection_weight,
    zoa_obscuration_mask,
)

__all__ = [
    "SurveyFootprint",
    "SURVEY_FOOTPRINTS",
    "get_survey_footprint",
    "is_inside_footprint",
    "valid_velocity_range",
    "relative_detection_weight",
    "zoa_obscuration_mask",
]
