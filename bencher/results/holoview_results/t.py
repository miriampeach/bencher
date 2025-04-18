from __future__ import annotations
import logging
from typing import List, Optional
import panel as pn
import holoviews as hv
from param import Parameter
from functools import partial
import hvplot.xarray  # noqa pylint: disable=duplicate-code,unused-import
import xarray as xr

from bencher.utils import (
    hmap_canonical_input,
    get_nearest_coords,
    get_nearest_coords1D,
    listify,
)
from bencher.results.panel_result import PanelResult
from bencher.results.bench_result_base import ReduceType
from bencher.plotting.plot_filter import PlotFilter, VarRange
from bencher.variables.results import ResultVar, ResultImage, ResultVideo
from bencher.results.holoview_results.holoview_result import HoloviewResult


class BarResult(HoloviewResult):
    