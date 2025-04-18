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


class CurveResult(HoloviewResult):
    def to_curve(self, result_var: Parameter = None, override: bool = True, **kwargs):
        return self.filter(
            self.to_curve_ds,
            float_range=VarRange(1, 1),
            cat_range=VarRange(0, None),
            repeats_range=VarRange(2, None),
            reduce=ReduceType.REDUCE,
            # reduce=ReduceType.MINMAX,
            target_dimension=2,
            result_var=result_var,
            result_types=(ResultVar),
            override=override,
            **kwargs,
        )

    def to_curve_ds(
        self, dataset: xr.Dataset, result_var: Parameter, **kwargs
    ) -> Optional[hv.Curve]:
        hvds = hv.Dataset(dataset)
        title = self.title_from_ds(dataset, result_var, **kwargs)
        # print(result_var.name)
        # print( dataset)
        pt = hv.Overlay()
        # find pairs of {var_name} {var_name}_std to plot the line and their spreads.
        var = result_var.name
        std_var = f"{var}_std"
        pt *= hvds.to(hv.Curve, vdims=var, label=var).opts(title=title, **kwargs)
        # Only create a Spread if the matching _std variable exists
        if std_var in dataset.data_vars:
            pt *= hvds.to(hv.Spread, vdims=[var, std_var])

        # for var in dataset.data_vars:
        #     print(var)
        #     if not var.endswith("_std"):
        #         std_var = f"{var}_std"
        #         pt *= hvds.to(hv.Curve, vdims=var, label=var).opts(title=title, **kwargs)
        #         #Only create a Spread if the matching _std variable exists
        #         if std_var in dataset.data_vars:
        #             pt *= hvds.to(hv.Spread, vdims=[var, std_var])

        return pt.opts(legend_position="right")
