from __future__ import annotations
from typing import Optional
import panel as pn
from param import Parameter
import hvplot.xarray  # noqa pylint: disable=duplicate-code,unused-import
import hvplot.pandas  # noqa pylint: disable=duplicate-code,unused-import
import xarray as xr

from bencher.results.panel_result import PanelResult
from bencher.results.bench_result_base import ReduceType

from bencher.plotting.plot_filter import VarRange
from bencher.variables.results import ResultVar


class ExplorerResult(PanelResult):
    def to_plot(self,**kwargs) -> pn.pane.Pane:
        """Produces a hvplot explorer instance to explore the generated dataset
        see: https://hvplot.holoviz.org/getting_started/explorer.html

        Returns:
            pn.pane.Pane: A dynamic pane for exploring a dataset
        """

        if len(self.bench_cfg.input_vars) > 0:
            return self.to_xarray().hvplot.explorer()

        # For some reason hvplot doesn't like 1D datasets in xarray, so convert to pandas which it has no problem with
        # TODO look into why this is, its probably due to how I am setting up the indexing in xarray.
        return self.to_pandas().hvplot.explorer()
