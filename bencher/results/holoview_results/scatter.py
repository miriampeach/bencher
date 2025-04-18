from __future__ import annotations
from typing import Optional
import panel as pn
import holoviews as hv
from param import Parameter
import xarray as xr

import hvplot.xarray  # noqa pylint: disable=duplicate-code,unused-import
import hvplot.pandas  # noqa pylint: disable=duplicate-code,unused-import
from bencher.results.bench_result_base import ReduceType

from bencher.plotting.plot_filter import VarRange
from bencher.variables.results import ResultVar


from bencher.results.holoview_result import HoloviewResult


class ScatterResult(HoloviewResult):
    def to_scatter(
        self, result_var: Parameter = None, override: bool = True, **kwargs
    ) -> Optional[pn.panel]:
        return self.filter(
            self.to_scatter_ds,
            float_range=VarRange(0, 0),
            cat_range=VarRange(0, None),
            repeats_range=VarRange(2, None),
            reduce=ReduceType.NONE,
            target_dimension=2,
            result_var=result_var,
            result_types=(ResultVar),
            override=override,
            **kwargs,
        )

    def to_scatter_ds(self, dataset: xr.Dataset, result_var: Parameter, **kwargs) -> hv.Scatter:
        by = None
        if self.plt_cnt_cfg.cat_cnt >= 2:
            by = self.plt_cnt_cfg.cat_vars[1].name
        # print(dataset)
        da_plot = dataset[result_var.name]
        # da_plot = dataset
        # print(da_plot)
        print("by", by)
        title = self.title_from_ds(da_plot, result_var, **kwargs)
        time_widget_args = self.time_widget(title)
        print(da_plot)
        # return da_plot.hvplot.box(by=by, **time_widget_args, **kwargs)
        # return da_plot.hvplot.box( **time_widget_args, **kwargs)
        return da_plot.hvplot.scatter(
            y=result_var.name, x="repeat", by=by, **time_widget_args, **kwargs
        ).opts(jitter=0.1)
