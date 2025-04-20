"""Distribution plot classes for visualizing benchmark results.

This module provides various visualization classes for showing the distribution 
of benchmark data through different plot types:

- DistributionResult: Base class with common functionality for distribution plots
- BoxWhiskerResult: Creates box and whisker plots showing median, quartiles, and outliers
- ViolinResult: Creates violin plots showing probability density and distribution shape
- ScatterJitterResult: Creates scatter plots with jitter to show individual data points
"""

from bencher.results.holoview_results.distribution_result.distribution_result import (
    DistributionResult,
)
from bencher.results.holoview_results.distribution_result.box_whisker_result import BoxWhiskerResult
from bencher.results.holoview_results.distribution_result.violin_result import ViolinResult
from bencher.results.holoview_results.distribution_result.scatter_jitter_result import (
    ScatterJitterResult,
)

__all__ = ["DistributionResult", "BoxWhiskerResult", "ViolinResult", "ScatterJitterResult"]
