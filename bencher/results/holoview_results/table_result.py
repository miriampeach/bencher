from __future__ import annotations
from typing import Optional
import panel as pn
from param import Parameter
import xarray as xr
import holoviews as hv
from bencher.results.bench_result_base import ReduceType
from bencher.plotting.plot_filter import VarRange
from bencher.variables.results import ResultVar
from bencher.results.holoview_results.holoview_result import HoloviewResult


class TableResult(HoloviewResult):
    def to_plot(self, **kwargs) -> hv.Table:  # pylint:disable=unused-argument
        """Convert the dataset to a Table visualization.

        Returns:
            hv.Table: A HoloViews Table object.
        """
        return self.to_hv_type(hv.Table, ReduceType.SQUEEZE)
