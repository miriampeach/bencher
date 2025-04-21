from __future__ import annotations
from typing import Optional
import panel as pn
from param import Parameter
import xarray as xr

from bencher.results.bench_result_base import ReduceType
from bencher.plotting.plot_filter import VarRange
from bencher.variables.results import ResultVar
from bencher.results.holoview_results.holoview_result import HoloviewResult


class TabulatorResult(HoloviewResult):
    def to_plot(self, **kwargs) -> pn.widgets.Tabulator:  # pylint:disable=unused-argument
        """Create an interactive table visualization of the data.

        Passes the data to the panel Tabulator type to display an interactive table.
        See https://panel.holoviz.org/reference/widgets/Tabulator.html for extra options.

        Args:
            **kwargs: Additional parameters to pass to the Tabulator constructor.

        Returns:
            pn.widgets.Tabulator: An interactive table widget.
        """
        return pn.widgets.Tabulator(self.to_pandas())
