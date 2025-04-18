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
    def to_bar(
        self, result_var: Parameter = None, override: bool = True, **kwargs
    ) -> Optional[pn.panel]:
        return self.filter(
            self.to_bar_ds,
            float_range=VarRange(0, 0),
            cat_range=VarRange(0, None),
            repeats_range=VarRange(1, 1),
            panel_range=VarRange(0, None),
            reduce=ReduceType.SQUEEZE,
            target_dimension=2,
            result_var=result_var,
            result_types=(ResultVar),
            override=override,
            **kwargs,
        )

    def to_bar_ds(self, dataset: xr.Dataset, result_var: Parameter = None, **kwargs):
        by = None
        if self.plt_cnt_cfg.cat_cnt >= 2:
            by = self.plt_cnt_cfg.cat_vars[1].name
        da_plot = dataset[result_var.name]
        title = self.title_from_ds(da_plot, result_var, **kwargs)
        time_widget_args = self.time_widget(title)
        return da_plot.hvplot.bar(by=by, **time_widget_args, **kwargs)
